"""
Agent Manager Service - Agent lifecycle and adapter management.

Responsibilities:
- Manage adapter instances (create, cache, destroy)
- Route tasks to appropriate adapter
- Platform health checking
"""
from collections.abc import Callable

from app.adapters.base import AgentAdapter
from app.adapters.codex import CodexAdapter
from app.adapters.llm_provider import LLMProviderAdapter
from app.adapters.mock import MockAdapter
from app.adapters.opencode import OpenCodeAdapter


class AgentManagerService:
    """Manages Agent adapters and routes tasks."""

    def __init__(self, factories: dict[str, Callable[[], AgentAdapter]] | None = None):
        self._adapters: dict[str, AgentAdapter] = {}
        self._factories = factories or {
            "mock": MockAdapter,
            "llm": LLMProviderAdapter,
            "opencode": OpenCodeAdapter,
            "codex": CodexAdapter,
        }

    async def get_adapter(self, platform_id: str):
        """Get or create an adapter instance for the given platform."""
        if platform_id not in self._factories:
            raise ValueError(f"Unsupported platform: {platform_id}")
        if platform_id not in self._adapters:
            self._adapters[platform_id] = self._factories[platform_id]()
        return self._adapters[platform_id]

    async def dispatch_task(self, platform_id: str, instruction: str, work_dir: str, context: dict | None = None):
        """Dispatch a task to the agent's platform adapter."""
        adapter = await self.get_adapter(platform_id)
        async for event in adapter.run_task(work_dir, instruction, context or {}):
            yield event

    async def resolve_adapter(self, platform_id: str, excluded: set[str] | None = None) -> tuple[AgentAdapter, str]:
        """Resolve a healthy platform while preserving Planner semantics."""
        excluded = excluded or set()
        candidates = []
        for candidate in (platform_id, "llm", "mock"):
            if candidate in self._factories and candidate not in candidates and candidate not in excluded:
                candidates.append(candidate)
        for candidate in candidates:
            adapter = await self.get_adapter(candidate)
            if await adapter.health_check():
                return adapter, candidate
        raise RuntimeError("No healthy agent adapter is available")

    async def check_health(self, platform_id: str) -> bool:
        """Check if a platform is available."""
        try:
            adapter = await self.get_adapter(platform_id)
        except ValueError:
            return False
        return await adapter.health_check()
