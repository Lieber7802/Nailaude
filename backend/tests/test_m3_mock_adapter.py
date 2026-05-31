from pathlib import Path

import pytest

from app.adapters.mock import MockAdapter
from app.services.orchestrator import OrchestratorService


@pytest.mark.asyncio
async def test_mock_adapter_materializes_generated_file_for_write_workspace(tmp_path):
    adapter = MockAdapter(response_delay=0)

    events = [
        event
        async for event in adapter.run_task(
            str(tmp_path),
            "build demo",
            {"workspace": {"accessMode": "write"}},
        )
    ]

    assert any(event.type == "file_created" for event in events)
    assert Path(tmp_path, "index.html").exists()


@pytest.mark.asyncio
async def test_mock_planner_uses_read_access_when_conversation_has_no_workspace():
    conversation = type("Conversation", (), {"participant_ids": ["agent-1"], "work_dir": ""})()
    agent = type("Agent", (), {"id": "agent-1", "name": "Builder"})()

    result = await OrchestratorService().build_mock_planner_result(conversation, "review", [], [agent])

    assert result["tasks"][0]["accessMode"] == "read"
