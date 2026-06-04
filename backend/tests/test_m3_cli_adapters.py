import asyncio
import json
import shutil
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import pytest

from app.adapters.codex import CodexAdapter, codex_sandbox_mode, resolve_codex_binary
from app.adapters.opencode import OpenCodeAdapter
from app.schemas.conversation import WORKSPACE_ROOT
from app.services.process_pool import ProcessPoolError, ProcessResult


class CapturingPool:
    def __init__(self):
        self.cancel_event = None
        self.command = None
        self.cwd = None
        self.env = None
        self.config = ""

    async def run(self, command, cwd, timeout=None, cancel_event=None, env=None, stdin_text=None):
        self.cancel_event = cancel_event
        self.command = command
        self.cwd = cwd
        self.env = env
        self.stdin_text = stdin_text
        if env and env.get("CODEX_HOME"):
            config_path = Path(env["CODEX_HOME"]) / "config.toml"
            if config_path.exists():
                self.config = config_path.read_text(encoding="utf-8")
        return ProcessResult(stdout="ok", stderr="", returncode=0)


class CodexJsonPool(CapturingPool):
    async def run(self, command, cwd, timeout=None, cancel_event=None, env=None, stdin_text=None):
        self.cancel_event = cancel_event
        self.command = command
        self.cwd = cwd
        self.env = env
        self.stdin_text = stdin_text
        if env and env.get("CODEX_HOME"):
            config_path = Path(env["CODEX_HOME"]) / "config.toml"
            if config_path.exists():
                self.config = config_path.read_text(encoding="utf-8")
        return ProcessResult(
            stdout="\n".join(
                [
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {"type": "agent_message", "text": "Created the page."},
                        }
                    ),
                    json.dumps(
                        {
                            "type": "item.completed",
                            "item": {"type": "agent_message", "text": "Final summary."},
                        }
                    ),
                ]
            ),
            stderr="",
            returncode=0,
        )


class OpenCodeJsonPool(CapturingPool):
    async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
        self.cancel_event = cancel_event
        self.command = command
        self.cwd = cwd
        self.env = env
        return ProcessResult(
            stdout="\n".join(
                [
                    json.dumps({"type": "message.delta", "delta": "Built "}),
                    json.dumps({"type": "message.delta", "delta": "the feature."}),
                    json.dumps({"type": "session.idle"}),
                ]
            ),
            stderr="",
            returncode=0,
        )


class OpenCodeRawEventPool(CapturingPool):
    async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
        self.cancel_event = cancel_event
        self.command = command
        self.cwd = cwd
        self.env = env
        return ProcessResult(
            stdout="\n".join(
                [
                    json.dumps({"type": "tool.start", "tool": "read", "path": "src/App.tsx"}),
                    json.dumps({"type": "tool.start", "tool": "edit", "path": "src/App.tsx"}),
                    json.dumps({"type": "unknown.raw", "payload": {"large": ["internal", "trace"]}}),
                    json.dumps({"type": "session.idle", "sessionID": "abc"}),
                ]
            ),
            stderr="",
            returncode=0,
        )


class OpenCodeObjectMessagePool(CapturingPool):
    async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
        self.cancel_event = cancel_event
        self.command = command
        self.cwd = cwd
        self.env = env
        return ProcessResult(
            stdout="\n".join(
                [
                    json.dumps(
                        {
                            "type": "message",
                            "message": {
                                "id": "msg-1",
                                "sessionID": "session-raw",
                                "role": "assistant",
                                "content": [
                                    {"type": "text", "text": "Wrote README.md with the project notes."}
                                ],
                            },
                        }
                    ),
                    json.dumps(
                        {
                            "type": "message.part.updated",
                            "part": {
                                "type": "tool",
                                "tool": "write",
                                "input": {"content": "# Very long raw file content"},
                            },
                        }
                    ),
                    json.dumps({"type": "session.idle", "sessionID": "session-raw"}),
                ]
            ),
            stderr="",
            returncode=0,
        )


class OpenCodeToolReadTextPool(CapturingPool):
    async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
        self.cancel_event = cancel_event
        self.command = command
        self.cwd = cwd
        self.env = env
        return ProcessResult(
            stdout="\n".join(
                [
                    json.dumps(
                        {
                            "type": "message.part.updated",
                            "part": {
                                "type": "text",
                                "text": (
                                    "232: \n"
                                    "233:     <div class=\"stats\">\n"
                                    "248:   <script>\n"
                                    "458: </html>\n\n"
                                    "(End of file - total 458 lines)\n"
                                    "</content>\",\"metadata\":{\"preview\":\"<!DOCTYPE html>\\n<html lang=\\\"zh-CN\\\">\","
                                    "\"sessionID\":\"ses_raw\""
                                ),
                            },
                        }
                    ),
                    json.dumps({"type": "session.idle", "sessionID": "ses_raw"}),
                ]
            ),
            stderr="",
            returncode=0,
        )


class OpenCodeAssistantCodeBlockPool(CapturingPool):
    async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
        self.cancel_event = cancel_event
        self.command = command
        self.cwd = cwd
        self.env = env
        Path(cwd, "src").mkdir(exist_ok=True)
        Path(cwd, "src", "App.tsx").write_text(
            "export default function App() {\n"
            "  return <main className=\"todo-shell\">Todo</main>\n"
            "}\n",
            encoding="utf-8",
        )
        return ProcessResult(
            stdout="\n".join(
                [
                    json.dumps(
                        {
                            "type": "message.part.updated",
                            "part": {
                                "type": "text",
                                "text": (
                                    "```tsx\n"
                                    "export default function App() {\n"
                                    "  return <main className=\"todo-shell\">Todo</main>\n"
                                    "}\n"
                                    "```\n"
                                ),
                            },
                        }
                    ),
                    json.dumps({"type": "session.idle", "sessionID": "code-block"}),
                ]
            ),
            stderr="",
            returncode=0,
        )


class OpenCodePreviewRepairPool(CapturingPool):
    def __init__(self):
        super().__init__()
        self.commands = []

    async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
        self.commands.append(command)
        self.command = command
        self.cwd = cwd
        if len(self.commands) == 1:
            Path(cwd, "README.md").write_text("# Notes only\n", encoding="utf-8")
            return ProcessResult(
                stdout=json.dumps({"type": "session.idle", "sessionID": "first"}),
                stderr="",
                returncode=0,
            )
        Path(cwd, "index.html").write_text("<!doctype html><h1>天气小程序</h1>\n", encoding="utf-8")
        return ProcessResult(
            stdout=json.dumps({"type": "message.delta", "delta": "已补充可预览页面。"}),
            stderr="",
            returncode=0,
        )


class FakeOpenCodeServerRunner:
    def __init__(self):
        self.work_dir = None
        self.prompt = None
        self.model = None
        self.env = None
        self.cancel_event = None

    async def run_message(self, *, work_dir, prompt, model, env, cancel_event=None):
        self.work_dir = work_dir
        self.prompt = prompt
        self.model = model
        self.env = env
        self.cancel_event = cancel_event
        Path(work_dir, "index.html").write_text("<!doctype html><h1>OK</h1>", encoding="utf-8")
        return [
            {"type": "reasoning", "text": "The user wants a tiny page."},
            {"type": "text", "text": "OpenCode server final summary."},
        ]


@asynccontextmanager
async def fake_bridge_factory():
    yield type("Bridge", (), {"base_url": "http://127.0.0.1:12345", "token": "bridge-token"})()


@pytest.mark.asyncio
@pytest.mark.parametrize("adapter_type", [CodexAdapter, OpenCodeAdapter])
async def test_cli_adapter_passes_runtime_cancel_event_to_process_pool(adapter_type):
    pool = CapturingPool()
    cancel_event = asyncio.Event()
    kwargs = {"bridge_factory": fake_bridge_factory} if adapter_type is CodexAdapter else {}
    adapter = adapter_type(pool=pool, binary_path="agent-cli", **kwargs)

    events = [event async for event in adapter.run_task(".", "work", {"_cancel_event": cancel_event})]

    assert [event.type for event in events] == ["text_delta", "done"]
    assert pool.cancel_event is cancel_event


@pytest.mark.asyncio
async def test_codex_adapter_uses_current_exec_json_cli(tmp_path):
    pool = CodexJsonPool()
    adapter = CodexAdapter(pool=pool, binary_path="codex", bridge_factory=fake_bridge_factory)

    events = [event async for event in adapter.run_task(str(tmp_path), "build", {"taskId": "task-1"})]

    assert pool.cwd == str(tmp_path)
    assert Path(pool.command[0]).name in {"codex", "codex.exe"}
    assert pool.command[1:4] == ["--ask-for-approval", "never", "exec"]
    assert "--json" in pool.command
    assert "--cd" in pool.command
    assert str(tmp_path) in pool.command
    assert pool.command[pool.command.index("--sandbox") + 1] == codex_sandbox_mode()
    assert events[0].type == "text_delta"
    assert "Final summary." in events[0].content
    assert events[-1].type == "done"


@pytest.mark.asyncio
async def test_opencode_adapter_uses_deepseek_json_run_cli(tmp_path):
    pool = OpenCodeJsonPool()
    adapter = OpenCodeAdapter(pool=pool, binary_path="opencode")

    events = [event async for event in adapter.run_task(str(tmp_path), "build", {"taskId": "task-1"})]

    assert pool.cwd == str(tmp_path)
    assert pool.command[:3] == ["opencode", "run", "--format"]
    assert "json" in pool.command
    assert "--model" in pool.command
    assert "deepseek/deepseek-v4-flash" in pool.command
    assert "--dir" in pool.command
    assert str(tmp_path) in pool.command
    assert "--dangerously-skip-permissions" in pool.command
    assert events[0].type == "text_delta"
    assert events[0].content == "Built the feature."
    assert events[-1].type == "done"


@pytest.mark.asyncio
async def test_opencode_adapter_resolves_relative_workspace_from_project_root():
    workspace_name = f"pytest-relative-opencode-{uuid.uuid4()}"
    work_dir = WORKSPACE_ROOT / workspace_name
    work_dir.mkdir(parents=True, exist_ok=True)
    try:
        pool = OpenCodeJsonPool()
        adapter = OpenCodeAdapter(pool=pool, binary_path="opencode")

        events = [event async for event in adapter.run_task(f"workspaces/{workspace_name}", "build", {})]

        assert pool.cwd == str(work_dir)
        assert str(work_dir) in pool.command
        assert events[-1].type == "done"
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_opencode_adapter_passes_deepseek_env_to_child_process(tmp_path, monkeypatch):
    pool = OpenCodeJsonPool()
    adapter = OpenCodeAdapter(pool=pool, binary_path="opencode")
    monkeypatch.setattr("app.adapters.opencode.settings.DEEPSEEK_API_KEY", "test-deepseek-key")
    monkeypatch.setattr("app.adapters.opencode.settings.DEEPSEEK_BASE_URL", "https://api.deepseek.test")
    monkeypatch.setattr("app.adapters.opencode.settings.DEEPSEEK_MODEL", "deepseek-test")

    events = [event async for event in adapter.run_task(str(tmp_path), "build", {"taskId": "task-1"})]

    assert events[-1].type == "done"
    assert pool.env["DEEPSEEK_API_KEY"] == "test-deepseek-key"
    assert pool.env["DEEPSEEK_BASE_URL"] == "https://api.deepseek.test"
    assert pool.env["DEEPSEEK_MODEL"] == "deepseek-test"


@pytest.mark.asyncio
async def test_opencode_adapter_summarizes_unknown_json_events_instead_of_streaming_raw(tmp_path):
    pool = OpenCodeRawEventPool()
    adapter = OpenCodeAdapter(pool=pool, binary_path="opencode")

    events = [event async for event in adapter.run_task(str(tmp_path), "build", {"taskId": "task-1"})]

    text_event = events[0]
    assert text_event.type == "text_delta"
    assert "OpenCode 已完成本次执行。" in text_event.content
    assert "正在查看项目文件。" in text_event.content
    assert "正在修改相关文件。" in text_event.content
    assert "unknown.raw" not in text_event.content
    assert "sessionID" not in text_event.content
    assert events[-1].type == "done"


@pytest.mark.asyncio
async def test_opencode_adapter_filters_malformed_protocol_fragments_from_chat(tmp_path):
    class ProtocolFragmentPool(CapturingPool):
        async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
            self.cwd = cwd
            return ProcessResult(
                stdout=(
                    'euMsedvHUG0cnSx","part":{"id":"prt_e872aa350001lgMWK9AgxOwo1Z",'
                    '"reason":"tool-calls","messageID":"msg_e872a9bd8001mQshtNq4C0Dguw",'
                    '"sessionID":"ses_178d6c708ffeuMsedvHUG0cnSx","type":"step-finish",'
                    '"tokens":{"total":25332,"input":193,"output":163,"reasoning":16,'
                    '"cache":{"write":0,"read":24960}},"cost":0.000147028}}\n'
                ),
                stderr="",
                returncode=0,
            )

    adapter = OpenCodeAdapter(pool=ProtocolFragmentPool(), binary_path="opencode")

    events = [event async for event in adapter.run_task(str(tmp_path), "build", {})]

    text_events = [event for event in events if event.type == "text_delta"]
    assert text_events
    assert "OpenCode 已完成本次执行。" in text_events[0].content
    assert "sessionID" not in text_events[0].content
    assert "tokens" not in text_events[0].content
    assert "euMsedvHUG0cnSx" not in text_events[0].content


@pytest.mark.asyncio
async def test_opencode_adapter_generates_review_fallback_when_review_returns_no_text(tmp_path):
    Path(tmp_path, "index.html").write_text(
        "<!doctype html><html><body><input id=\"name\"><button>签到</button><script>"
        "const name = document.getElementById('name');"
        "localStorage.setItem('students', JSON.stringify([]));"
        "</script></body></html>",
        encoding="utf-8",
    )

    class ReviewProtocolOnlyPool(OpenCodeRawEventPool):
        async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
            self.cwd = cwd
            self.command = command
            return ProcessResult(
                stdout="\n".join(
                    [
                        json.dumps({"type": "tool.start", "tool": "read", "path": "index.html"}),
                        json.dumps({"type": "session.idle", "sessionID": "review-only"}),
                    ]
                ),
                stderr="",
                returncode=0,
            )

    adapter = OpenCodeAdapter(pool=ReviewProtocolOnlyPool(), binary_path="opencode")

    events = [
        event
        async for event in adapter.run_task(
            str(tmp_path),
            "Review index.html for quality, performance, and security issues.",
            {
                "task": {"accessMode": "read", "instruction": "Review index.html"},
                "workspace": {"accessMode": "read"},
                "navigationHints": {"inspectFirst": ["index.html"]},
            },
        )
    ]

    text_event = events[0]
    assert text_event.type == "text_delta"
    assert "审查完成" in text_event.content
    assert "index.html" in text_event.content
    assert "localStorage" in text_event.content
    assert "未检测到工作区文件变更" not in text_event.content
    assert [event.type for event in events] == ["text_delta", "done"]


@pytest.mark.asyncio
async def test_opencode_adapter_does_not_stream_object_messages_or_tool_payloads(tmp_path):
    pool = OpenCodeObjectMessagePool()
    adapter = OpenCodeAdapter(pool=pool, binary_path="opencode")

    events = [event async for event in adapter.run_task(str(tmp_path), "build", {"taskId": "task-1"})]

    text_event = events[0]
    assert text_event.type == "text_delta"
    assert "OpenCode 已完成本次执行。" in text_event.content
    assert "正在修改相关文件。" in text_event.content
    assert "sessionID" not in text_event.content
    assert "session-raw" not in text_event.content
    assert "Very long raw file content" not in text_event.content
    assert "'content':" not in text_event.content
    assert '"content":' not in text_event.content


@pytest.mark.asyncio
async def test_opencode_adapter_summarizes_tool_read_text_instead_of_streaming_file_content(tmp_path):
    pool = OpenCodeToolReadTextPool()
    adapter = OpenCodeAdapter(pool=pool, binary_path="opencode")

    events = [event async for event in adapter.run_task(str(tmp_path), "review", {"taskId": "task-1"})]

    text_event = events[0]
    assert text_event.type == "text_delta"
    assert "OpenCode 已完成本次执行。" in text_event.content
    assert "正在查看项目文件。" in text_event.content
    assert "<script>" not in text_event.content
    assert "</content>" not in text_event.content
    assert "metadata" not in text_event.content
    assert "sessionID" not in text_event.content
    assert "458 lines" not in text_event.content


@pytest.mark.asyncio
async def test_opencode_adapter_summarizes_assistant_code_blocks_instead_of_streaming_raw_code(tmp_path):
    pool = OpenCodeAssistantCodeBlockPool()
    adapter = OpenCodeAdapter(pool=pool, binary_path="opencode")

    events = [event async for event in adapter.run_task(str(tmp_path), "build app", {"taskId": "task-1"})]

    text_event = events[0]
    assert text_event.type == "text_delta"
    assert "OpenCode 已完成本次执行。" in text_event.content
    assert "检测到 1 个文件变更，已生成对应产物卡片。" in text_event.content
    assert "```tsx" not in text_event.content
    assert "export default function App" not in text_event.content
    assert "todo-shell" not in text_event.content
    file_events = [event for event in events if event.type == "file_created"]
    assert file_events[0].content == "src/App.tsx"
    assert file_events[0].metadata["files"][0]["language"] == "tsx"


@pytest.mark.asyncio
async def test_opencode_prompt_requires_preview_entry_for_app_generation(tmp_path):
    pool = OpenCodeJsonPool()
    adapter = OpenCodeAdapter(pool=pool, binary_path="opencode")

    await anext(
        adapter.run_task(
            str(tmp_path),
            "请实现一个天气小程序，右侧需要预览",
            {
                "task": {
                    "title": "生成天气小程序",
                    "objective": "生成可预览天气小程序",
                    "instruction": "生成天气小程序",
                    "accessMode": "write",
                },
                "workspace": {"accessMode": "write"},
            },
        )
    )

    prompt = pool.command[-1]
    assert "必须创建或更新 index.html" in prompt
    assert "不要只创建 README.md" in prompt
    assert "右侧预览" in prompt


def test_opencode_prompt_requires_preview_entry_for_system_implementation_requests():
    adapter = OpenCodeAdapter(pool=OpenCodeJsonPool(), binary_path="opencode")

    assert adapter._should_require_preview_entry(
        "根据需求文档实现学生课程签到系统的完整代码。",
        {"workspace": {"accessMode": "write"}, "task": {"accessMode": "write"}},
    )


@pytest.mark.parametrize(
    "instruction,task",
    [
        (
            "分析学生课程签到系统需求，输出 PRD.md、SPEC.md 和 CHECKLIST.md。",
            {
                "id": "requirements",
                "title": "需求分析与PRD",
                "objective": "整理需求、项目SPEC和验收checklist",
                "instruction": "输出 Markdown 文档，不创建 index.html。",
                "accessMode": "write",
            },
        ),
        (
            "编写 README.md，说明系统功能、运行方式和已知限制。",
            {
                "id": "readme",
                "title": "README 文档",
                "objective": "整理最终 README",
                "instruction": "输出 README.md，不创建 index.html。",
                "accessMode": "write",
            },
        ),
    ],
)
def test_opencode_prompt_does_not_require_preview_for_document_tasks(instruction, task):
    adapter = OpenCodeAdapter(pool=OpenCodeJsonPool(), binary_path="opencode")

    assert not adapter._should_require_preview_entry(
        instruction,
        {"workspace": {"accessMode": "write"}, "task": task},
    )


@pytest.mark.asyncio
async def test_opencode_repairs_preview_request_when_first_run_only_writes_readme(tmp_path):
    pool = OpenCodePreviewRepairPool()
    adapter = OpenCodeAdapter(pool=pool, binary_path="opencode")

    events = [
        event
        async for event in adapter.run_task(
            str(tmp_path),
            "请实现一个天气小程序，右侧需要预览",
            {
                "task": {
                    "title": "生成天气小程序",
                    "objective": "生成可预览天气小程序",
                    "instruction": "生成天气小程序",
                    "accessMode": "write",
                },
                "workspace": {"accessMode": "write"},
            },
        )
    ]

    assert len(pool.commands) == 2
    assert "上一轮执行没有创建可供 AgentHub 右侧预览的 HTML 入口" in pool.commands[1][-1]
    created_files = [event.content for event in events if event.type == "file_created"]
    assert created_files == ["README.md", "index.html"]
    index_event = next(event for event in events if event.content == "index.html")
    assert index_event.metadata["files"][0]["language"] == "html"
    assert events[-1].type == "done"


def test_opencode_extracts_nested_server_text_without_reasoning_noise():
    payload = {
        "parts": [
            {"type": "reasoning", "text": "The user wants me to reply exactly OPENCODE_SERVER_WSL_OK."},
            {"type": "text", "text": "OPENCODE_SERVER_WSL_OK"},
        ]
    }

    adapter = OpenCodeAdapter(pool=OpenCodeJsonPool(), binary_path="opencode")

    assert adapter._extract_server_text(payload) == "OPENCODE_SERVER_WSL_OK"


@pytest.mark.asyncio
async def test_opencode_adapter_prefers_server_runner_for_model_text_and_file_events(tmp_path, monkeypatch):
    runner = FakeOpenCodeServerRunner()
    cancel_event = asyncio.Event()
    adapter = OpenCodeAdapter(binary_path="opencode", server_runner=runner)
    monkeypatch.setattr("app.adapters.opencode.settings.DEEPSEEK_API_KEY", "test-deepseek-key")
    monkeypatch.setattr("app.adapters.opencode.settings.DEEPSEEK_BASE_URL", "https://api.deepseek.test")

    events = [
        event
        async for event in adapter.run_task(
            str(tmp_path),
            "Create index.html",
            {"task": {"accessMode": "write"}, "workspace": {"accessMode": "write"}, "_cancel_event": cancel_event},
        )
    ]

    assert runner.work_dir == str(tmp_path)
    assert runner.model == "deepseek/deepseek-v4-flash"
    assert runner.env["DEEPSEEK_API_KEY"] == "test-deepseek-key"
    assert runner.cancel_event is cancel_event
    assert events[0].type == "text_delta"
    assert events[0].content == "OpenCode server final summary."
    assert [event.content for event in events if event.type == "file_created"] == ["index.html"]
    assert events[-1].type == "done"


@pytest.mark.asyncio
async def test_codex_adapter_uses_isolated_home_and_loopback_bridge(tmp_path, monkeypatch):
    pool = CodexJsonPool()
    codex_home_root = tmp_path / "codex-homes"
    monkeypatch.setenv("CODEX_THREAD_ID", "desktop-thread")
    monkeypatch.setenv("AGENTHUB_CODEX_HOME_ROOT", str(codex_home_root))
    adapter = CodexAdapter(pool=pool, binary_path="codex", bridge_factory=fake_bridge_factory)

    events = [event async for event in adapter.run_task(str(tmp_path), "build", {})]

    assert events[-1].type == "done"
    assert pool.env["AGENTHUB_CODEX_BRIDGE_TOKEN"] == "bridge-token"
    assert pool.env["CODEX_HOME"] != str(tmp_path)
    assert Path(pool.env["CODEX_HOME"]).parent == codex_home_root
    assert pool.command[-1] == "-"
    assert pool.stdin_text and "AgentHub handoff context follows as JSON" in pool.stdin_text
    assert "CODEX_THREAD_ID" not in pool.env
    assert 'base_url = "http://127.0.0.1:12345"' in pool.config
    assert 'env_key = "AGENTHUB_CODEX_BRIDGE_TOKEN"' in pool.config
    assert 'wire_api = "responses"' in pool.config
    assert "[windows]" not in pool.config


def test_resolve_codex_binary_prefers_latest_windows_desktop_cache(tmp_path, monkeypatch):
    local_app_data = tmp_path / "LocalAppData"
    older = local_app_data / "OpenAI" / "Codex" / "bin" / "old" / "codex.exe"
    latest = local_app_data / "OpenAI" / "Codex" / "bin" / "latest" / "codex.exe"
    older.parent.mkdir(parents=True)
    latest.parent.mkdir(parents=True)
    older.write_text("", encoding="utf-8")
    latest.write_text("", encoding="utf-8")
    older.touch()
    latest.touch()
    monkeypatch.setenv("LOCALAPPDATA", str(local_app_data))
    monkeypatch.setattr("app.adapters.codex.shutil.which", lambda _: None)
    monkeypatch.setattr("app.adapters.codex._windows_cli_candidates", lambda: [latest, older])

    assert resolve_codex_binary("codex", platform="nt") == str(latest)


def test_codex_sandbox_mode_uses_windows_full_access_fallback_only_on_windows():
    assert codex_sandbox_mode("nt") == "danger-full-access"
    assert codex_sandbox_mode("posix") == "workspace-write"


@pytest.mark.asyncio
async def test_codex_adapter_emits_file_events_for_workspace_changes(tmp_path):
    existing = tmp_path / "existing.txt"
    existing.write_text("old", encoding="utf-8")

    class FileChangingPool(CodexJsonPool):
        async def run(self, command, cwd, timeout=None, cancel_event=None, env=None, stdin_text=None):
            (tmp_path / "new.py").write_text("print('hello')\n", encoding="utf-8")
            existing.write_text("new", encoding="utf-8")
            return await super().run(command, cwd, timeout, cancel_event, env, stdin_text)

    adapter = CodexAdapter(pool=FileChangingPool(), binary_path="codex", bridge_factory=fake_bridge_factory)

    events = [event async for event in adapter.run_task(str(tmp_path), "edit files", {})]

    file_events = [event for event in events if event.type in {"file_created", "file_modified"}]
    assert [event.type for event in file_events] == ["file_modified", "file_created"]
    assert file_events[0].content == "existing.txt"
    assert file_events[0].metadata["oldContent"] == "old"
    assert file_events[0].metadata["newContent"] == "new"
    assert file_events[1].content == "new.py"
    assert file_events[1].metadata["files"] == [
        {"name": "new.py", "content": "print('hello')\n", "language": "python"}
    ]


@pytest.mark.asyncio
async def test_opencode_adapter_emits_file_events_for_workspace_changes(tmp_path):
    existing = tmp_path / "existing.txt"
    existing.write_text("old", encoding="utf-8")

    class FileChangingPool(OpenCodeJsonPool):
        async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
            (tmp_path / "new.ts").write_text("export const ok = true;\n", encoding="utf-8")
            existing.write_text("new", encoding="utf-8")
            return await super().run(command, cwd, timeout, cancel_event, env)

    adapter = OpenCodeAdapter(pool=FileChangingPool(), binary_path="opencode")

    events = [event async for event in adapter.run_task(str(tmp_path), "edit files", {})]

    file_events = [event for event in events if event.type in {"file_created", "file_modified"}]
    assert [event.type for event in file_events] == ["file_modified", "file_created"]
    assert file_events[0].content == "existing.txt"
    assert file_events[0].metadata["oldContent"] == "old"
    assert file_events[0].metadata["newContent"] == "new"
    assert file_events[1].content == "new.ts"
    assert file_events[1].metadata["files"] == [
        {"name": "new.ts", "content": "export const ok = true;\n", "language": "typescript"}
    ]


@pytest.mark.asyncio
async def test_opencode_raw_event_summary_mentions_artifacts_for_file_changes(tmp_path):
    class FileChangingPool(OpenCodeRawEventPool):
        async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
            (tmp_path / "new.ts").write_text("export const ok = true;\n", encoding="utf-8")
            return await super().run(command, cwd, timeout, cancel_event, env)

    adapter = OpenCodeAdapter(pool=FileChangingPool(), binary_path="opencode")

    events = [event async for event in adapter.run_task(str(tmp_path), "edit files", {})]

    assert events[0].type == "text_delta"
    assert "检测到 1 个文件变更，已生成对应产物卡片。" in events[0].content
    assert "export const ok" not in events[0].content
    assert [event.type for event in events if event.type == "file_created"] == ["file_created"]


@pytest.mark.asyncio
async def test_opencode_adapter_emits_file_events_for_changes_written_before_timeout(tmp_path):
    class TimeoutAfterWritePool(CapturingPool):
        async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
            Path(cwd, "index.html").write_text("<!doctype html><h1>学生签到</h1>\n", encoding="utf-8")
            raise ProcessPoolError("process timed out")

    adapter = OpenCodeAdapter(pool=TimeoutAfterWritePool(), binary_path="opencode")

    events = [event async for event in adapter.run_task(str(tmp_path), "build page", {})]

    assert events[0].type == "text_delta"
    assert "检测到 1 个文件变更，已生成对应产物卡片。" in events[0].content
    file_events = [event for event in events if event.type == "file_created"]
    assert len(file_events) == 1
    assert file_events[0].content == "index.html"
    assert file_events[0].metadata["files"] == [
        {"name": "index.html", "content": "<!doctype html><h1>学生签到</h1>\n", "language": "html"}
    ]
    error_events = [event for event in events if event.type == "error"]
    assert error_events[0].content == "process timed out"
