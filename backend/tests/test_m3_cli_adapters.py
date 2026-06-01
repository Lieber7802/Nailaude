import asyncio
import json

import pytest

from app.adapters.codex import CodexAdapter
from app.adapters.opencode import OpenCodeAdapter
from app.services.process_pool import ProcessResult


class CapturingPool:
    def __init__(self):
        self.cancel_event = None
        self.command = None
        self.cwd = None

    async def run(self, command, cwd, timeout=None, cancel_event=None):
        self.cancel_event = cancel_event
        self.command = command
        self.cwd = cwd
        return ProcessResult(stdout="ok", stderr="", returncode=0)


class CodexJsonPool(CapturingPool):
    async def run(self, command, cwd, timeout=None, cancel_event=None):
        self.cancel_event = cancel_event
        self.command = command
        self.cwd = cwd
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
    async def run(self, command, cwd, timeout=None, cancel_event=None):
        self.cancel_event = cancel_event
        self.command = command
        self.cwd = cwd
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


@pytest.mark.asyncio
@pytest.mark.parametrize("adapter_type", [CodexAdapter, OpenCodeAdapter])
async def test_cli_adapter_passes_runtime_cancel_event_to_process_pool(adapter_type):
    pool = CapturingPool()
    cancel_event = asyncio.Event()
    adapter = adapter_type(pool=pool, binary_path="agent-cli")

    events = [event async for event in adapter.run_task(".", "work", {"_cancel_event": cancel_event})]

    assert [event.type for event in events] == ["text_delta", "done"]
    assert pool.cancel_event is cancel_event


@pytest.mark.asyncio
async def test_codex_adapter_uses_current_exec_json_cli(tmp_path):
    pool = CodexJsonPool()
    adapter = CodexAdapter(pool=pool, binary_path="codex")

    events = [event async for event in adapter.run_task(str(tmp_path), "build", {"taskId": "task-1"})]

    assert pool.cwd == str(tmp_path)
    assert pool.command[:4] == ["codex", "--ask-for-approval", "never", "exec"]
    assert "--json" in pool.command
    assert "--cd" in pool.command
    assert str(tmp_path) in pool.command
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
async def test_codex_adapter_emits_file_events_for_workspace_changes(tmp_path):
    existing = tmp_path / "existing.txt"
    existing.write_text("old", encoding="utf-8")

    class FileChangingPool(CodexJsonPool):
        async def run(self, command, cwd, timeout=None, cancel_event=None):
            (tmp_path / "new.py").write_text("print('hello')\n", encoding="utf-8")
            existing.write_text("new", encoding="utf-8")
            return await super().run(command, cwd, timeout, cancel_event)

    adapter = CodexAdapter(pool=FileChangingPool(), binary_path="codex")

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
        async def run(self, command, cwd, timeout=None, cancel_event=None):
            (tmp_path / "new.ts").write_text("export const ok = true;\n", encoding="utf-8")
            existing.write_text("new", encoding="utf-8")
            return await super().run(command, cwd, timeout, cancel_event)

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
