import asyncio

import pytest

from app.adapters.codex import CodexAdapter
from app.adapters.opencode import OpenCodeAdapter
from app.services.process_pool import ProcessResult


class CapturingPool:
    def __init__(self):
        self.cancel_event = None

    async def run(self, command, cwd, timeout=None, cancel_event=None):
        self.cancel_event = cancel_event
        return ProcessResult(stdout="ok", stderr="", returncode=0)


@pytest.mark.asyncio
@pytest.mark.parametrize("adapter_type", [CodexAdapter, OpenCodeAdapter])
async def test_cli_adapter_passes_runtime_cancel_event_to_process_pool(adapter_type):
    pool = CapturingPool()
    cancel_event = asyncio.Event()
    adapter = adapter_type(pool=pool, binary_path="agent-cli")

    events = [event async for event in adapter.run_task(".", "work", {"_cancel_event": cancel_event})]

    assert [event.type for event in events] == ["text_delta", "done"]
    assert pool.cancel_event is cancel_event
