import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path

import pytest

from app.adapters.codex import CodexAdapter, codex_sandbox_mode, resolve_codex_binary
from app.adapters.opencode import OpenCodeAdapter
from app.services.process_pool import ProcessResult


class CapturingPool:
    def __init__(self):
        self.cancel_event = None
        self.command = None
        self.cwd = None
        self.env = None
        self.config = ""

    async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
        self.cancel_event = cancel_event
        self.command = command
        self.cwd = cwd
        self.env = env
        if env and env.get("CODEX_HOME"):
            config_path = Path(env["CODEX_HOME"]) / "config.toml"
            if config_path.exists():
                self.config = config_path.read_text(encoding="utf-8")
        return ProcessResult(stdout="ok", stderr="", returncode=0)


class CodexJsonPool(CapturingPool):
    async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
        self.cancel_event = cancel_event
        self.command = command
        self.cwd = cwd
        self.env = env
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
async def test_codex_adapter_uses_isolated_home_and_loopback_bridge(tmp_path, monkeypatch):
    pool = CodexJsonPool()
    monkeypatch.setenv("CODEX_THREAD_ID", "desktop-thread")
    adapter = CodexAdapter(pool=pool, binary_path="codex", bridge_factory=fake_bridge_factory)

    events = [event async for event in adapter.run_task(str(tmp_path), "build", {})]

    assert events[-1].type == "done"
    assert pool.env["AGENTHUB_CODEX_BRIDGE_TOKEN"] == "bridge-token"
    assert pool.env["CODEX_HOME"] != str(tmp_path)
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
        async def run(self, command, cwd, timeout=None, cancel_event=None, env=None):
            (tmp_path / "new.py").write_text("print('hello')\n", encoding="utf-8")
            existing.write_text("new", encoding="utf-8")
            return await super().run(command, cwd, timeout, cancel_event, env)

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
