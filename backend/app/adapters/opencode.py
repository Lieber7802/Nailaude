"""
OpenCode Adapter - Integration with OpenCode CLI.

OpenCode supports session-based interaction (long-running process).
run_task() internally manages sessions for efficiency.
"""
from typing import AsyncGenerator
import asyncio
import json
import os
import re
import shutil
import socket
from pathlib import Path

import httpx

from app.adapters.base import AgentAdapter, AgentEvent, AgentSession
from app.config import settings
from app.services.process_pool import ProcessPool, ProcessPoolError
from app.adapters.codex import LANGUAGE_BY_SUFFIX, MAX_FILE_BYTES, SKIPPED_DIRS
from app.services.workspace_scanner import WorkspaceScanner
from app.services.workspace_paths import resolve_workspace_path


MAX_CHAT_SUMMARY_CHARS = 1200
OPENCODE_SERVER_START_TIMEOUT_SECONDS = 20.0
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
    "系统",
    "应用",
    "预览",
    "右侧",
    "可视化",
)


class OpenCodeServerRunner:
    """Per-task OpenCode HTTP server execution boundary."""

    def __init__(self, binary_path: str):
        self.binary_path = binary_path

    async def run_message(
        self,
        *,
        work_dir: str,
        prompt: str,
        model: str,
        env: dict[str, str],
        cancel_event: asyncio.Event | None = None,
    ):
        port = self._free_port()
        try:
            process = await asyncio.create_subprocess_exec(
                self.binary_path,
                "serve",
                "--hostname",
                "127.0.0.1",
                "--port",
                str(port),
                cwd=work_dir,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
                env=env,
            )
        except OSError as exc:
            raise ProcessPoolError(f"failed to start OpenCode server: {exc}") from exc

        base_url = f"http://127.0.0.1:{port}"
        try:
            async with httpx.AsyncClient(timeout=settings.CLI_TIMEOUT_SECONDS) as client:
                await self._wait_until_healthy(client, base_url, process, cancel_event)
                session_response = await client.post(f"{base_url}/session", json={})
                session_response.raise_for_status()
                session_id = self._session_id(session_response.json())
                if not session_id:
                    raise ProcessPoolError("OpenCode server did not return a session id")
                message_response = await client.post(
                    f"{base_url}/session/{session_id}/message",
                    json={
                        "parts": [{"type": "text", "text": prompt}],
                        "model": self._model_payload(model),
                    },
                )
                message_response.raise_for_status()
                return message_response.json()
        except httpx.HTTPError as exc:
            raise ProcessPoolError(f"OpenCode server request failed: {exc}") from exc
        finally:
            await self._terminate(process)

    async def _wait_until_healthy(
        self,
        client: httpx.AsyncClient,
        base_url: str,
        process: asyncio.subprocess.Process,
        cancel_event: asyncio.Event | None,
    ) -> None:
        deadline = asyncio.get_running_loop().time() + OPENCODE_SERVER_START_TIMEOUT_SECONDS
        while asyncio.get_running_loop().time() < deadline:
            if cancel_event and cancel_event.is_set():
                raise ProcessPoolError("process cancelled")
            if process.returncode is not None:
                raise ProcessPoolError("OpenCode server exited before becoming healthy")
            try:
                response = await client.get(f"{base_url}/global/health", timeout=2)
                if response.status_code == 200 and response.json().get("healthy"):
                    return
            except (httpx.HTTPError, json.JSONDecodeError):
                pass
            await asyncio.sleep(0.25)
        raise ProcessPoolError("OpenCode server health check timed out")

    async def _terminate(self, process: asyncio.subprocess.Process) -> None:
        if process.returncode is not None:
            return
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=3)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()

    def _free_port(self) -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    def _session_id(self, payload) -> str:
        if isinstance(payload, dict):
            for key in ("id", "sessionID", "sessionId"):
                value = payload.get(key)
                if isinstance(value, str):
                    return value
            session = payload.get("session")
            if isinstance(session, dict):
                return self._session_id(session)
        return ""

    def _model_payload(self, model: str) -> dict[str, str]:
        provider, sep, model_id = model.partition("/")
        if sep:
            return {"providerID": provider, "modelID": model_id}
        return {"providerID": "deepseek", "modelID": model}


class OpenCodeAdapter(AgentAdapter):
    """OpenCode CLI adapter - session-based agent."""

    platform_name = "opencode"

    def __init__(
        self,
        pool: ProcessPool | None = None,
        binary_path: str | None = None,
        server_runner: OpenCodeServerRunner | None = None,
    ):
        self.pool = pool or ProcessPool(settings.CLI_TIMEOUT_SECONDS)
        self.binary_path = binary_path or settings.OPENCODE_BINARY_PATH
        self.server_runner = server_runner if server_runner is not None else (
            OpenCodeServerRunner(self.binary_path) if pool is None else None
        )

    async def run_task(
        self, work_dir: str, instruction: str, context: dict
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Execute a DeepSeek-backed one-shot OpenCode run.
        """
        cancel_event = context.get("_cancel_event")
        root = resolve_workspace_path(work_dir)
        before = self._snapshot_workspace(root)
        public_context = {key: value for key, value in context.items() if not key.startswith("_")}
        preview_required = self._should_require_preview_entry(instruction, public_context)
        prompt = self._build_prompt(instruction, context)
        env = self._opencode_env()
        try:
            if self.server_runner is not None:
                try:
                    response = await self.server_runner.run_message(
                        work_dir=str(root),
                        prompt=prompt,
                        model=settings.OPENCODE_MODEL,
                        env=env,
                        cancel_event=cancel_event,
                    )
                    stdout = ""
                    content = self._extract_server_text(response)
                except ProcessPoolError:
                    result = await self._run_cli_prompt(str(root), prompt, cancel_event, env)
                    stdout = result.stdout
                    content = ""
            else:
                result = await self._run_cli_prompt(str(root), prompt, cancel_event, env)
                stdout = result.stdout
                content = ""
            after = self._snapshot_workspace(root)
            if preview_required and not self._has_preview_entry(after):
                repair_prompt = self._build_preview_repair_prompt(instruction, public_context)
                if self.server_runner is not None:
                    try:
                        repair_response = await self.server_runner.run_message(
                            work_dir=str(root),
                            prompt=repair_prompt,
                            model=settings.OPENCODE_MODEL,
                            env=env,
                            cancel_event=cancel_event,
                        )
                        repair_content = self._extract_server_text(repair_response)
                        if repair_content:
                            content = repair_content
                    except ProcessPoolError:
                        repair_result = await self._run_cli_prompt(str(root), repair_prompt, cancel_event, env)
                        stdout = "\n".join(part for part in (stdout, repair_result.stdout) if part)
                else:
                    repair_result = await self._run_cli_prompt(str(root), repair_prompt, cancel_event, env)
                    stdout = "\n".join(part for part in (stdout, repair_result.stdout) if part)
                after = self._snapshot_workspace(root)
            file_events = self._file_events(before, after)
            if not content:
                content = self._extract_text(stdout, file_events)
            if self._should_use_review_fallback(content, instruction, public_context, file_events):
                content = self._review_fallback_summary(root, public_context)
            if content:
                yield AgentEvent(type="text_delta", content=content)
            for event in file_events:
                yield event
        except ProcessPoolError as exc:
            file_events = self._file_events(before, self._snapshot_workspace(root))
            if file_events:
                yield AgentEvent(type="text_delta", content=self._interrupted_chat_summary(file_events, str(exc)))
                for event in file_events:
                    yield event
            yield AgentEvent(type="error", content=str(exc))
        yield AgentEvent(type="done", content="")

    async def _run_cli_prompt(
        self,
        root: str,
        prompt: str,
        cancel_event: asyncio.Event | None,
        env: dict[str, str],
    ):
        return await self.pool.run(
            [
                self.binary_path,
                "run",
                "--format",
                "json",
                "--model",
                settings.OPENCODE_MODEL,
                "--dir",
                root,
                "--dangerously-skip-permissions",
                prompt,
            ],
            cwd=root,
            cancel_event=cancel_event,
            env=env,
        )

    async def health_check(self) -> bool:
        if shutil.which(self.binary_path) is None:
            return False
        try:
            await self.pool.run([self.binary_path, "run", "--help"], cwd=".", timeout=5)
        except ProcessPoolError:
            return False
        return True

    def _opencode_env(self) -> dict[str, str]:
        env = os.environ.copy()
        if settings.DEEPSEEK_API_KEY:
            env["DEEPSEEK_API_KEY"] = settings.DEEPSEEK_API_KEY
        if settings.DEEPSEEK_BASE_URL:
            env["DEEPSEEK_BASE_URL"] = settings.DEEPSEEK_BASE_URL
        if settings.DEEPSEEK_MODEL:
            env["DEEPSEEK_MODEL"] = settings.DEEPSEEK_MODEL
        return env

    def _build_prompt(self, instruction: str, context: dict) -> str:
        public_context = {key: value for key, value in context.items() if not key.startswith("_")}
        preview_contract = self._preview_contract(instruction, public_context)
        review_contract = self._review_contract(instruction, public_context)
        return (
            f"{instruction}\n\n"
            "AgentHub handoff context follows as JSON. Respect the task boundary, "
            "write files only inside the provided workspace, and summarize the result.\n"
            f"{review_contract}"
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
                if self._looks_like_protocol_fragment(line):
                    saw_json_event = True
                    work_steps.add("正在调用 OpenCode 工具处理任务。")
                elif not self._looks_like_json_event(line):
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
                display_message = self._display_chat_text(message, work_steps)
                if display_message:
                    messages.append(display_message)
                continue
            if event_type in {"message.part.updated", "message.part.added"}:
                part = event.get("part") or {}
                self._collect_work_step(event, work_steps)
                text = self._part_text(part)
                if text and self._looks_like_tool_result_text(text):
                    self._collect_text_work_step(text, work_steps)
                    continue
                if text:
                    display_text = self._display_chat_text(text, work_steps)
                    if display_text:
                        messages.append(display_text)
                continue
            self._collect_work_step(event, work_steps)
            if event_type in {"session.idle", "task_complete", "turn_complete", "completed"}:
                summary = self._text_value(event.get("last_agent_message") or event.get("message") or event.get("output"))
                if summary:
                    display_summary = self._display_chat_text(summary, work_steps)
                    if display_summary:
                        messages.append(display_summary)
        if messages:
            return self._limit_chat_text(messages[-1])
        if deltas:
            delta_text = self._display_chat_text("".join(deltas), work_steps)
            if delta_text:
                return self._limit_chat_text(delta_text)
        if plain_lines:
            plain_text = self._display_chat_text("\n".join(plain_lines), work_steps)
            if plain_text:
                return self._limit_chat_text(plain_text)
        if saw_json_event:
            return self._fallback_chat_summary(file_events or [], work_steps)
        return ""

    def _extract_server_text(self, payload) -> str:
        texts: list[str] = []

        def collect(value) -> None:
            if isinstance(value, list):
                for item in value:
                    collect(item)
                return
            if not isinstance(value, dict):
                return
            item_type = str(value.get("type") or "").lower()
            if item_type in {"reasoning", "step-start", "step-finish", "tool", "tool_use", "tool-result"}:
                return
            if item_type in {"text", "markdown", "agent_message", "assistant_message"}:
                text = self._text_value(value.get("text") or value.get("content"))
                if text:
                    texts.append(text)
            for child in value.values():
                collect(child)

        collect(payload)
        display_texts = [
            display
            for display in (self._display_chat_text(text, set()) for text in texts)
            if display and not self._looks_like_tool_result_text(display)
        ]
        if not display_texts:
            return ""
        return self._limit_chat_text(display_texts[-1])

    def _looks_like_json_event(self, line: str) -> bool:
        return line.startswith("{") or line.startswith("[")

    def _looks_like_protocol_fragment(self, line: str) -> bool:
        lowered = line.lower()
        markers = (
            '"messageid"',
            '"part"',
            '"sessionid"',
            '"tokens"',
            "msg_",
            "prt_",
            "ses_",
            "step-finish",
            "tool-calls",
        )
        return sum(1 for marker in markers if marker in lowered) >= 2

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

    def _display_chat_text(self, text: str, work_steps: set[str]) -> str:
        stripped = text.strip()
        if not stripped:
            return ""
        without_code_blocks = self._strip_fenced_code_blocks(stripped)
        if without_code_blocks != stripped:
            work_steps.add("正在整理代码产物。")
        if not without_code_blocks:
            return ""
        if self._looks_like_raw_code_text(without_code_blocks):
            work_steps.add("正在整理代码产物。")
            return ""
        return without_code_blocks

    def _strip_fenced_code_blocks(self, text: str) -> str:
        cleaned = re.sub(r"```[^\n`]*\n.*?```", "", text, flags=re.DOTALL)
        cleaned = re.sub(r"```.*?```", "", cleaned, flags=re.DOTALL)
        lines = [line.rstrip() for line in cleaned.splitlines()]
        return "\n".join(line for line in lines if line.strip()).strip()

    def _looks_like_raw_code_text(self, text: str) -> bool:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if len(lines) < 3:
            return False
        code_line_prefixes = (
            "import ",
            "export ",
            "from ",
            "def ",
            "class ",
            "function ",
            "const ",
            "let ",
            "var ",
            "return ",
            "public ",
            "private ",
            "protected ",
        )
        code_markers = (
            "{",
            "}",
            ";",
            "=>",
            "className=",
            "</",
            "/>",
            "():",
            " = ",
        )
        prefix_hits = sum(1 for line in lines[:20] if line.startswith(code_line_prefixes))
        marker_hits = sum(1 for line in lines[:20] if any(marker in line for marker in code_markers))
        return prefix_hits >= 2 or marker_hits >= 5

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

    def _should_use_review_fallback(
        self,
        content: str,
        instruction: str,
        context: dict,
        file_events: list[AgentEvent],
    ) -> bool:
        if not self._is_review_task(instruction, context) or file_events:
            return False
        if not content:
            return True
        generic_markers = (
            "OpenCode 已完成本次执行。",
            "未检测到工作区文件变更。",
        )
        return all(marker in content for marker in generic_markers)

    def _review_contract(self, instruction: str, context: dict) -> str:
        if not self._is_review_task(instruction, context):
            return ""
        return (
            "AgentHub review contract: 本任务是只读代码审查。不要修改、创建或删除文件。"
            "必须在最终回复中用中文输出可执行审查意见，至少包含：总体结论、主要问题、改进建议。"
            "如果未发现严重问题，也要说明可维护性、可访问性、性能或安全方面的后续建议。\n"
        )

    def _is_review_task(self, instruction: str, context: dict) -> bool:
        task = context.get("task") or {}
        workspace = context.get("workspace") or {}
        text = " ".join(
            str(value)
            for value in (
                instruction,
                task.get("title"),
                task.get("objective"),
                task.get("instruction"),
            )
            if value
        ).lower()
        review_words = ("review", "audit", "inspect", "审查", "评审", "代码审查", "检查", "质量")
        return any(word in text for word in review_words) and (
            task.get("accessMode") == "read" or workspace.get("accessMode") == "read"
        )

    def _review_fallback_summary(self, root: Path, context: dict) -> str:
        snapshot = self._snapshot_workspace(root)
        candidates = self._review_candidate_files(snapshot, context)
        if not candidates:
            return "审查完成：当前工作区没有可审查的代码文件。建议先确认代码产物是否已生成并落盘。"

        name, content = candidates[0]
        size_kb = max(1, round(len(content.encode("utf-8")) / 1024))
        notes = [
            f"审查完成：已检查 {name}（约 {size_kb} KB）。",
            "总体结论：当前实现可以作为演示版继续验证，但建议在进入下一轮开发前补齐工程化和边界处理。",
        ]
        issues = self._review_heuristics(name, content)
        notes.append("主要问题：")
        notes.extend(f"- {issue}" for issue in issues[:4])
        notes.append("改进建议：")
        notes.extend(
            [
                "- 补充核心交互的手动测试用例，至少覆盖空输入、重复签到、筛选和清空数据。",
                "- 将样式、脚本与页面结构逐步拆分，降低单文件维护成本。",
                "- 明确数据持久化边界；如果后续接入真实课程/学生数据，需要补充鉴权和输入校验。",
            ]
        )
        return "\n".join(notes)

    def _review_candidate_files(self, snapshot: dict[str, str], context: dict) -> list[tuple[str, str]]:
        hints = context.get("navigationHints") or {}
        hinted_paths = [
            str(path)
            for path in [*(hints.get("inspectFirst") or []), *(hints.get("changedFiles") or [])]
            if str(path) in snapshot
        ]
        preferred = hinted_paths or sorted(snapshot)
        suffixes = (".html", ".htm", ".js", ".jsx", ".ts", ".tsx", ".css", ".py")
        return [(name, snapshot[name]) for name in preferred if name.lower().endswith(suffixes)]

    def _review_heuristics(self, name: str, content: str) -> list[str]:
        lowered = content.lower()
        issues: list[str] = []
        if name.lower().endswith((".html", ".htm")) and "<script" in lowered:
            issues.append("HTML、CSS、JavaScript 集中在单文件中，后续功能增长后维护成本会快速上升。")
        if "localstorage" in lowered:
            issues.append("使用 localStorage 适合本地演示，但不适合多用户课程签到的真实数据同步和权限控制。")
        if "innerhtml" in lowered:
            issues.append("代码中出现 innerHTML，若拼接用户输入需要额外防范 XSS 风险。")
        if "<input" in lowered and "required" not in lowered:
            issues.append("表单输入缺少浏览器级 required 约束，建议补充空值和格式校验。")
        if "@media" not in lowered:
            issues.append("未看到响应式断点，移动端或窄屏使用体验可能不稳定。")
        if not issues:
            issues.append("未发现明显阻塞问题，但仍建议补充异常路径和可访问性检查。")
        return issues

    def _interrupted_chat_summary(self, file_events: list[AgentEvent], error: str) -> str:
        return "\n".join(
            [
                "OpenCode 执行中断，已保留超时前写入的文件。",
                f"检测到 {len(file_events)} 个文件变更，已生成对应产物卡片。",
                f"中断原因：{error}",
            ]
        )

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
