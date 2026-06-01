"""
Codex Adapter - Integration with OpenAI Codex CLI.

Codex uses a one-shot task model (one process per task).
run_task() spawns a new process each time.
"""
from typing import AsyncGenerator
import json
import shutil
from pathlib import Path

from app.adapters.base import AgentAdapter, AgentEvent
from app.config import settings
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


class CodexAdapter(AgentAdapter):
    """Codex CLI adapter - one-shot task execution."""

    platform_name = "codex"

    def __init__(self, pool: ProcessPool | None = None, binary_path: str | None = None):
        self.pool = pool or ProcessPool(settings.CLI_TIMEOUT_SECONDS)
        self.binary_path = binary_path or settings.CODEX_BINARY_PATH

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
            result = await self.pool.run(
                [
                    self.binary_path,
                    "--ask-for-approval",
                    "never",
                    "exec",
                    "--json",
                    "--cd",
                    str(root),
                    "--sandbox",
                    "workspace-write",
                    "--skip-git-repo-check",
                    prompt,
                ],
                cwd=str(root),
                cancel_event=cancel_event,
            )
            content = self._extract_text(result.stdout)
            if content:
                yield AgentEvent(type="text_delta", content=content)
            after = self._snapshot_workspace(root)
            for event in self._file_events(before, after):
                yield event
        except ProcessPoolError as exc:
            yield AgentEvent(type="error", content=str(exc))
        yield AgentEvent(type="done", content="")

    async def health_check(self) -> bool:
        if shutil.which(self.binary_path) is None:
            return False
        try:
            await self.pool.run([self.binary_path, "--help"], cwd=".", timeout=5)
        except ProcessPoolError:
            return False
        return True

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
