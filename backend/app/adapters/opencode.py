"""
OpenCode Adapter - Integration with OpenCode CLI.

OpenCode supports session-based interaction (long-running process).
run_task() internally manages sessions for efficiency.
"""
from typing import AsyncGenerator
import json
import shutil
from pathlib import Path

from app.adapters.base import AgentAdapter, AgentEvent, AgentSession
from app.config import settings
from app.services.process_pool import ProcessPool, ProcessPoolError
from app.adapters.codex import LANGUAGE_BY_SUFFIX, MAX_FILE_BYTES, SKIPPED_DIRS
from app.services.workspace_scanner import WorkspaceScanner


MAX_CHAT_SUMMARY_CHARS = 1200
PREVIEW_REQUEST_KEYWORDS = (
    "app",
    "application",
    "page",
    "webpage",
    "website",
    "preview",
    "html",
    "页面",
    "网页",
    "小程序",
    "应用",
    "预览",
    "右侧",
    "可视化",
)


class OpenCodeAdapter(AgentAdapter):
    """OpenCode CLI adapter - session-based agent."""

    platform_name = "opencode"

    def __init__(self, pool: ProcessPool | None = None, binary_path: str | None = None):
        self.pool = pool or ProcessPool(settings.CLI_TIMEOUT_SECONDS)
        self.binary_path = binary_path or settings.OPENCODE_BINARY_PATH

    async def run_task(
        self, work_dir: str, instruction: str, context: dict
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Execute a DeepSeek-backed one-shot OpenCode run.
        """
        cancel_event = context.get("_cancel_event")
        root = Path(work_dir).expanduser().resolve()
        before = self._snapshot_workspace(root)
        public_context = {key: value for key, value in context.items() if not key.startswith("_")}
        preview_required = self._should_require_preview_entry(instruction, public_context)
        prompt = self._build_prompt(instruction, context)
        try:
            result = await self.pool.run(
                [
                    self.binary_path,
                    "run",
                    "--format",
                    "json",
                    "--model",
                    settings.OPENCODE_MODEL,
                    "--dir",
                    str(root),
                    "--dangerously-skip-permissions",
                    prompt,
                ],
                cwd=str(root),
                cancel_event=cancel_event,
            )
            after = self._snapshot_workspace(root)
            stdout = result.stdout
            if preview_required and not self._has_preview_entry(after):
                repair_result = await self.pool.run(
                    [
                        self.binary_path,
                        "run",
                        "--format",
                        "json",
                        "--model",
                        settings.OPENCODE_MODEL,
                        "--dir",
                        str(root),
                        "--dangerously-skip-permissions",
                        self._build_preview_repair_prompt(instruction, public_context),
                    ],
                    cwd=str(root),
                    cancel_event=cancel_event,
                )
                stdout = "\n".join(part for part in (stdout, repair_result.stdout) if part)
                after = self._snapshot_workspace(root)
            file_events = self._file_events(before, after)
            content = self._extract_text(stdout, file_events)
            if content:
                yield AgentEvent(type="text_delta", content=content)
            for event in file_events:
                yield event
        except ProcessPoolError as exc:
            yield AgentEvent(type="error", content=str(exc))
        yield AgentEvent(type="done", content="")

    async def health_check(self) -> bool:
        if shutil.which(self.binary_path) is None:
            return False
        try:
            await self.pool.run([self.binary_path, "run", "--help"], cwd=".", timeout=5)
        except ProcessPoolError:
            return False
        return True

    def _build_prompt(self, instruction: str, context: dict) -> str:
        public_context = {key: value for key, value in context.items() if not key.startswith("_")}
        preview_contract = self._preview_contract(instruction, public_context)
        return (
            f"{instruction}\n\n"
            "AgentHub handoff context follows as JSON. Respect the task boundary, "
            "write files only inside the provided workspace, and summarize the result.\n"
            f"{preview_contract}"
            f"{json.dumps(public_context, ensure_ascii=False, default=str)}"
        )

    def _extract_text(self, stdout: str, file_events: list[AgentEvent] | None = None) -> str:
        messages: list[str] = []
        deltas: list[str] = []
        plain_lines: list[str] = []
        work_steps: set[str] = set()
        saw_json_event = False
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                if not self._looks_like_json_event(line):
                    plain_lines.append(line)
                continue
            if not isinstance(event, dict):
                continue
            saw_json_event = True
            event_type = str(event.get("type") or "")
            delta = self._text_value(event.get("delta") or event.get("text") or event.get("content"))
            if event_type in {"message.delta", "message_delta", "assistant_delta", "agent_message_delta"} and delta:
                deltas.append(delta)
                continue
            message = self._text_value(event.get("message") or event.get("text") or event.get("content"))
            if event_type in {"message", "assistant_message", "agent_message"} and message:
                messages.append(message)
                continue
            if event_type in {"message.part.updated", "message.part.added"}:
                part = event.get("part") or {}
                self._collect_work_step(event, work_steps)
                text = self._part_text(part)
                if text and self._looks_like_tool_result_text(text):
                    self._collect_text_work_step(text, work_steps)
                    continue
                if text:
                    messages.append(text)
                continue
            self._collect_work_step(event, work_steps)
            if event_type in {"session.idle", "task_complete", "turn_complete", "completed"}:
                summary = self._text_value(event.get("last_agent_message") or event.get("message") or event.get("output"))
                if summary:
                    messages.append(summary)
        if messages:
            return self._limit_chat_text(messages[-1])
        if deltas:
            return self._limit_chat_text("".join(deltas))
        if plain_lines:
            return self._limit_chat_text("\n".join(plain_lines))
        if saw_json_event:
            return self._fallback_chat_summary(file_events or [], work_steps)
        return ""

    def _looks_like_json_event(self, line: str) -> bool:
        return line.startswith("{") or line.startswith("[")

    def _text_value(self, value) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            parts: list[str] = []
            for item in value:
                text = self._part_text(item)
                if text:
                    parts.append(text)
            return "\n".join(parts)
        return ""

    def _part_text(self, part) -> str:
        if isinstance(part, str):
            return part
        if not isinstance(part, dict):
            return ""
        if part.get("type") not in {None, "text", "markdown"}:
            return ""
        text = part.get("text") or part.get("content")
        return text if isinstance(text, str) else ""

    def _looks_like_tool_result_text(self, text: str) -> bool:
        stripped = text.strip()
        if not stripped:
            return False
        indicators = (
            "</content>",
            '"metadata"',
            "'metadata'",
            '"sessionID"',
            "'sessionID'",
            "(End of file - total",
            "<!DOCTYPE html",
            "<html",
            "<script",
        )
        if any(indicator in stripped for indicator in indicators):
            return True
        lines = stripped.splitlines()
        numbered_lines = sum(1 for line in lines[:20] if self._is_numbered_file_line(line))
        return numbered_lines >= 3

    def _is_numbered_file_line(self, line: str) -> bool:
        head, sep, tail = line.partition(":")
        return bool(sep and head.strip().isdigit() and (tail.startswith(" ") or tail == ""))

    def _collect_text_work_step(self, text: str, work_steps: set[str]) -> None:
        lowered = text.lower()
        if any(token in lowered for token in ("</content>", "(end of file - total", "<!doctype html", "<html")):
            work_steps.add("正在查看项目文件。")
        else:
            work_steps.add("正在处理工具输出。")

    def _collect_work_step(self, event: dict, work_steps: set[str]) -> None:
        event_type = str(event.get("type") or "").lower()
        payload = json.dumps(event, ensure_ascii=False, default=str).lower()
        if "tool" not in event_type and "tool" not in payload:
            return
        if any(name in payload for name in ("edit", "write", "patch", "create", "modify")):
            work_steps.add("正在修改相关文件。")
        elif any(name in payload for name in ("read", "grep", "glob", "list", "search")):
            work_steps.add("正在查看项目文件。")
        elif any(name in payload for name in ("bash", "shell", "command")):
            work_steps.add("正在运行必要命令。")
        else:
            work_steps.add("正在调用 OpenCode 工具处理任务。")

    def _fallback_chat_summary(self, file_events: list[AgentEvent], work_steps: set[str]) -> str:
        lines = ["OpenCode 已完成本次执行。"]
        lines.extend(sorted(work_steps))
        if file_events:
            lines.append(f"检测到 {len(file_events)} 个文件变更，已生成对应产物卡片。")
        else:
            lines.append("未检测到工作区文件变更。")
        return "\n".join(lines)

    def _limit_chat_text(self, text: str) -> str:
        normalized = text.strip()
        if len(normalized) <= MAX_CHAT_SUMMARY_CHARS:
            return normalized
        return f"{normalized[:MAX_CHAT_SUMMARY_CHARS].rstrip()}...\n（已截断，完整产物请查看下方卡片。）"

    def _preview_contract(self, instruction: str, context: dict) -> str:
        if not self._should_require_preview_entry(instruction, context):
            return ""
        return (
            "AgentHub preview contract: 用户要求的是可预览应用/页面/小程序。"
            "必须创建或更新 index.html 作为右侧预览入口，并把主要交互、样式和脚本放在可直接打开的前端文件中。"
            "不要只创建 README.md、说明文档或纯文字总结；README 只能作为补充。\n"
        )

    def _should_require_preview_entry(self, instruction: str, context: dict) -> bool:
        workspace = context.get("workspace") or {}
        task = context.get("task") or {}
        if workspace.get("accessMode") != "write" and task.get("accessMode") != "write":
            return False
        text = " ".join(
            str(value)
            for value in (
                instruction,
                task.get("title"),
                task.get("objective"),
                task.get("instruction"),
                " ".join(str(item) for item in task.get("acceptanceCriteria") or []),
            )
            if value
        ).lower()
        return any(keyword in text for keyword in PREVIEW_REQUEST_KEYWORDS)

    def _has_preview_entry(self, snapshot: dict[str, str]) -> bool:
        return any(name.lower().endswith((".html", ".htm")) for name in snapshot)

    def _build_preview_repair_prompt(self, instruction: str, context: dict) -> str:
        return (
            "上一轮执行没有创建可供 AgentHub 右侧预览的 HTML 入口。"
            "必须创建或更新 index.html，实现用户要求的可交互小程序/页面。"
            "不要只创建 README.md 或说明文字；必须产出可直接在浏览器 iframe 中打开的 index.html。\n\n"
            f"原始用户要求：{instruction}\n\n"
            "AgentHub handoff context follows as JSON.\n"
            f"{json.dumps(context, ensure_ascii=False, default=str)}"
        )

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
                snapshot[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8")
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

    async def start_session(self, work_dir: str, system_instruction: str) -> AgentSession:
        """Start an OpenCode session."""
        # TODO: implement
        raise NotImplementedError("OpenCode sessions not yet implemented")

    async def send_message(self, session: AgentSession, message: str) -> AsyncGenerator[AgentEvent, None]:
        """Send message to OpenCode session."""
        # TODO: implement
        yield AgentEvent(type="error", content="Not implemented")

    async def stop_session(self, session: AgentSession) -> None:
        """Stop OpenCode session."""
        # TODO: implement
        pass
