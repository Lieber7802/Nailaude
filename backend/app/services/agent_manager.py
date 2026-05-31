"""
Agent Manager Service - Agent lifecycle and adapter management.

Responsibilities:
- Manage adapter instances (create, cache, destroy)
- Route tasks to appropriate adapter
- Platform health checking
"""
from app.adapters.codex import CodexAdapter
from app.adapters.llm_provider import LLMProviderAdapter
from app.adapters.mock import MockAdapter
from app.adapters.opencode import OpenCodeAdapter


class AgentManagerService:
    """Manages Agent adapters and routes tasks."""

    def __init__(self):
        self._adapters: dict = {}

    async def get_adapter(self, platform_id: str):
        """Get or create an adapter instance for the given platform."""
        if platform_id in self._adapters:
            return self._adapters[platform_id]

        adapter = self._create_adapter(platform_id)
        self._adapters[platform_id] = adapter
        return adapter

    async def dispatch_task(self, platform_id: str, instruction: str, work_dir: str, context: dict | None = None):
        """Dispatch a task to the agent's platform adapter."""
        adapter = await self.get_adapter(platform_id)
        async for event in adapter.run_task(work_dir, instruction, context or {}):
            yield event

    async def check_health(self, platform_id: str) -> bool:
        """Check if a platform is available."""
        adapter = await self.get_adapter(platform_id)
        return await adapter.health_check()

    def _create_adapter(self, platform_id: str):
        if platform_id == "mock":
            return MockAdapter(response_delay=0)
        if platform_id == "llm":
            return LLMProviderAdapter()
        if platform_id == "opencode":
            return OpenCodeAdapter()
        if platform_id == "codex":
            return CodexAdapter()
        raise ValueError(f"Unsupported platform: {platform_id}")
