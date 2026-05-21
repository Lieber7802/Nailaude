"""
Agent Manager Service - Agent lifecycle and adapter management.

Responsibilities:
- Manage adapter instances (create, cache, destroy)
- Route tasks to appropriate adapter
- Platform health checking
"""


class AgentManagerService:
    """Manages Agent adapters and routes tasks."""

    def __init__(self):
        self._adapters: dict = {}

    async def get_adapter(self, platform_id: str):
        """Get or create an adapter instance for the given platform."""
        # TODO: implement adapter factory
        return None

    async def dispatch_task(self, agent_id: str, instruction: str, work_dir: str):
        """Dispatch a task to the agent's platform adapter."""
        # TODO: implement
        pass

    async def check_health(self, platform_id: str) -> bool:
        """Check if a platform is available."""
        # TODO: implement
        return False
