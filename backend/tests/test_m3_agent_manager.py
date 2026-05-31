import pytest

from app.adapters.base import AgentAdapter, AgentEvent
from app.services.agent_manager import AgentManagerService


class FakeAdapter(AgentAdapter):
    def __init__(self, healthy: bool, label: str):
        self.healthy = healthy
        self.label = label

    async def run_task(self, work_dir: str, instruction: str, context: dict):
        yield AgentEvent(type="text_delta", content=self.label)
        yield AgentEvent(type="done")

    async def health_check(self) -> bool:
        return self.healthy


@pytest.mark.asyncio
async def test_agent_manager_uses_requested_healthy_adapter():
    manager = AgentManagerService(
        factories={"codex": lambda: FakeAdapter(True, "codex"), "mock": lambda: FakeAdapter(True, "mock")}
    )

    adapter, selected_platform = await manager.resolve_adapter("codex")

    assert selected_platform == "codex"
    assert adapter.label == "codex"


@pytest.mark.asyncio
async def test_agent_manager_falls_back_when_requested_adapter_is_unhealthy():
    manager = AgentManagerService(
        factories={
            "codex": lambda: FakeAdapter(False, "codex"),
            "llm": lambda: FakeAdapter(False, "llm"),
            "mock": lambda: FakeAdapter(True, "mock"),
        }
    )

    adapter, selected_platform = await manager.resolve_adapter("codex")

    assert selected_platform == "mock"
    assert adapter.label == "mock"


@pytest.mark.asyncio
async def test_agent_manager_downgrades_unavailable_cli_to_llm():
    manager = AgentManagerService(
        factories={
            "codex": lambda: FakeAdapter(False, "codex"),
            "llm": lambda: FakeAdapter(True, "llm"),
            "mock": lambda: FakeAdapter(True, "mock"),
        }
    )

    adapter, selected_platform = await manager.resolve_adapter("codex")

    assert selected_platform == "llm"
    assert adapter.label == "llm"


@pytest.mark.asyncio
async def test_agent_manager_resolves_execution_fallback_without_retrying_failed_platform():
    manager = AgentManagerService(
        factories={
            "codex": lambda: FakeAdapter(True, "codex"),
            "llm": lambda: FakeAdapter(True, "llm"),
            "mock": lambda: FakeAdapter(True, "mock"),
        }
    )

    adapter, selected_platform = await manager.resolve_adapter("codex", excluded={"codex"})

    assert selected_platform == "llm"
    assert adapter.label == "llm"
