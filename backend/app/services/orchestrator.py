"""
Orchestrator Service - Task dispatch and coordination for group chats.

Responsibilities:
- Parse user intent (detect @mentions, analyze task)
- Build dispatch plan (which agents to invoke)
- Execute plan (call agents, collect results)
- Summarize and return to user
"""


class OrchestratorService:
    """Orchestrator for multi-agent task dispatch."""

    async def handle_message(self, conversation_id: str, content: str, mentions: list):
        """Main entry point: process a user message in group chat."""
        # TODO: implement intent parsing + dispatch
        pass

    async def _parse_intent(self, content: str, mentions: list) -> dict:
        """Use LLM to parse user intent."""
        # TODO: call Volcano API
        return {"action": "direct_dispatch", "agents": mentions}

    async def _build_dispatch_plan(self, intent: dict) -> dict:
        """Build execution plan based on parsed intent."""
        # TODO: implement
        return {"tasks": []}

    async def _execute_plan(self, plan: dict):
        """Execute the dispatch plan."""
        # TODO: implement
        pass
