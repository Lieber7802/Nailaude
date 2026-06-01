"""
Codex Adapter - Integration with OpenAI Codex CLI.

Codex uses a one-shot task model (one process per task).
run_task() spawns a new process each time.
"""
from typing import AsyncGenerator
import json
import os
import shutil
import tempfile
from pathlib import Path
from collections.abc import Callable

from app.adapters.base import AgentAdapter, AgentEvent
from app.config import settings
from app.services.deepseek_responses_bridge import DeepSeekResponsesBridge, DeepSeekResponsesBridgeError
from app.services.process_pool import ProcessPool, ProcessPoolError
from app.services.workspace_scanner import WorkspaceScanner


LANGUAGE_BY_SUFFIX = {
    ".css": "css",
    ".html": "html",
    ".js": "javascript",
    ".json": "json",
    ".jsx": "jsx",
    ".md": "markdown",
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".txt": "text",
}
SKIPPED_DIRS = {
    ".git",
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}
MAX_FILE_BYTES = 512_000


def _windows_cli_candidates() -> list[Path]:
    candidates: list[Path] = []
    if cli_path := os.environ.get("CODEX_CLI_PATH"):
        candidates.append(Path(cli_path))
    if local_app_data := os.environ.get("LOCALAPPDATA"):
        cache_root = Path(local_app_data) / "OpenAI" / "Codex" / "bin"
        if cache_root.exists():
            candidates.extend(sorted(cache_root.glob("*/codex.exe"), key=lambda path: path.stat().st_mtime, reverse=True))
    if user_profile := os.environ.get("USERPROFILE"):
        candidates.append(Path(user_profile) / ".codex" / ".sandbox-bin" / "codex.exe")
    return candidates


def resolve_codex_binary(configured_path: str, platform: str = os.name) -> str:
    if configured_path != "codex":
        return str(Path(configured_path).expanduser())
    if platform == "nt":
        for candidate in _windows_cli_candidates():
            if candidate.is_file():
                return str(candidate)
    return shutil.which(configured_path) or configured_path


def codex_sandbox_mode(platform: str = os.name) -> str:
    return "danger-full-access" if platform == "nt" else "workspace-write"


class CodexAdapter(AgentAdapter):
    """Codex CLI adapter - one-shot task execution."""

    platform_name = "codex"

    def __init__(
        self,
        pool: ProcessPool | None = None,
        binary_path: str | None = None,
        bridge_factory: Callable | None = None,
    ):
        self.pool = pool or ProcessPool(settings.CLI_TIMEOUT_SECONDS)
        self.binary_path = resolve_codex_binary(binary_path or settings.CODEX_BINARY_PATH)
        self.bridge_factory = bridge_factory or DeepSeekResponsesBridge

    async def run_task(
        self, work_dir: str, instruction: str, context: dict
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Execute a Codex one-shot task when a usable CLI is installed.
        """
        cancel_event = context.get("_cancel_event")
        root = Path(work_dir).expanduser().resolve()
        before = self._snapshot_workspace(root)
        prompt = self._build_prompt(instruction, context)
        try:
            async with self.bridge_factory() as bridge:
                with tempfile.TemporaryDirectory(prefix="agenthub-codex-") as codex_home:
                    self._write_isolated_config(Path(codex_home), bridge.base_url)
                    result = await self.pool.run(
                        [
                            self.binary_path,
                            "--ask-for-approval",
                            "never",
                            "exec",
                            "--ephemeral",
                            "--json",
                            "--cd",
                            str(root),
                            "--sandbox",
                            codex_sandbox_mode(),
                            "--skip-git-repo-check",
                            prompt,
                        ],
                        cwd=str(root),
                        cancel_event=cancel_event,
                        env=self._isolated_env(codex_home, bridge.token),
                    )
            content = self._extract_text(result.stdout)
            if content:
                yield AgentEvent(type="text_delta", content=content)
            after = self._snapshot_workspace(root)
            for event in self._file_events(before, after):
                yield event
        except (DeepSeekResponsesBridgeError, ProcessPoolError) as exc:
            yield AgentEvent(type="error", content=str(exc))
        yield AgentEvent(type="done", content="")

    async def health_check(self) -> bool:
        if not settings.DEEPSEEK_API_KEY or not self._binary_exists():
            return False
        try:
            await self.pool.run([self.binary_path, "--help"], cwd=".", timeout=5)
        except ProcessPoolError:
            return False
        return True

    def _write_isolated_config(self, codex_home: Path, bridge_base_url: str) -> None:
        config = (
            f"model = {json.dumps(settings.DEEPSEEK_MODEL)}\n"
            'model_provider = "agenthub_deepseek"\n\n'
            "[model_providers.agenthub_deepseek]\n"
            'name = "AgentHub DeepSeek Bridge"\n'
            f"base_url = {json.dumps(bridge_base_url)}\n"
            'env_key = "AGENTHUB_CODEX_BRIDGE_TOKEN"\n'
            'wire_api = "responses"\n'
            "request_max_retries = 0\n"
            "stream_max_retries = 0\n"
            "requires_openai_auth = false\n"
        )
        (codex_home / "config.toml").write_text(config, encoding="utf-8")

    def _isolated_env(self, codex_home: str, bridge_token: str) -> dict[str, str]:
        env = os.environ.copy()
        env["CODEX_HOME"] = codex_home
        env["AGENTHUB_CODEX_BRIDGE_TOKEN"] = bridge_token
        for name in ("CODEX_THREAD_ID", "CODEX_INTERNAL_ORIGINATOR_OVERRIDE"):
            env.pop(name, None)
        return env

    def _binary_exists(self) -> bool:
        path = Path(self.binary_path)
        return path.is_file() if path.is_absolute() else shutil.which(self.binary_path) is not None

    def _build_prompt(self, instruction: str, context: dict) -> str:
        public_context = {key: value for key, value in context.items() if not key.startswith("_")}
        return (
            f"{instruction}\n\n"
            "AgentHub handoff context follows as JSON. Respect the task boundary, "
            "write files only inside the provided workspace, and summarize the result.\n"
            f"{json.dumps(public_context, ensure_ascii=False, default=str)}"
        )

    def _extract_text(self, stdout: str) -> str:
        messages: list[str] = []
        deltas: list[str] = []
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                messages.append(line)
                continue
            if not isinstance(event, dict):
                continue
            event_type = str(event.get("type") or "")
            if event_type in {"agent_message_delta", "message_delta", "assistant_delta"}:
                delta = event.get("delta") or event.get("text") or event.get("content")
                if delta:
                    deltas.append(str(delta))
            elif event_type in {"agent_message", "assistant_message", "message"}:
                message = event.get("message") or event.get("text") or event.get("content")
                if message:
                    messages.append(str(message))
            elif event_type in {"item.completed", "item_completed"}:
                item = event.get("item") or {}
                if isinstance(item, dict) and item.get("type") == "agent_message" and item.get("text"):
                    messages.append(str(item["text"]))
            elif event_type in {"task_complete", "turn_complete", "completed"}:
                message = (
                    event.get("last_agent_message")
                    or event.get("message")
                    or event.get("output")
                    or event.get("result")
                )
                if message:
                    messages.append(str(message))
        if messages:
            return messages[-1]
        if deltas:
            return "".join(deltas)
        return stdout.strip()

    def _snapshot_workspace(self, root: Path) -> dict[str, str]:
        if not root.exists():
            return {}
        snapshot: dict[str, str] = {}
        scanner = WorkspaceScanner()
        for path in sorted(root.rglob("*")):
            if not path.is_file() or self._is_skipped(path, root):
                continue
            try:
                if scanner._sensitive(path.name):
                    continue
                if path.stat().st_size > MAX_FILE_BYTES:
                    continue
                relative = path.relative_to(root).as_posix()
                snapshot[relative] = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
        return snapshot

    def _file_events(self, before: dict[str, str], after: dict[str, str]) -> list[AgentEvent]:
        events: list[AgentEvent] = []
        for name in sorted(after):
            old_content = before.get(name)
            new_content = after[name]
            if old_content is None:
                events.append(self._file_event("file_created", name, new_content))
            elif old_content != new_content:
                events.append(self._file_event("file_modified", name, new_content, old_content=old_content))
        return events

    def _file_event(
        self,
        event_type: str,
        name: str,
        content: str,
        *,
        old_content: str | None = None,
    ) -> AgentEvent:
        language = LANGUAGE_BY_SUFFIX.get(Path(name).suffix.lower(), "text")
        metadata = {
            "title": name,
            "files": [{"name": name, "content": content, "language": language}],
            "previewUrl": None,
        }
        if old_content is not None:
            metadata["oldContent"] = old_content
            metadata["newContent"] = content
        return AgentEvent(type=event_type, content=name, metadata=metadata)

    def _is_skipped(self, path: Path, root: Path) -> bool:
        try:
            relative = path.relative_to(root)
        except ValueError:
            return True
        return any(part in SKIPPED_DIRS for part in relative.parts)
