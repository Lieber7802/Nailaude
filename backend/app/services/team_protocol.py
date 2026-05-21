"""
Team Protocol Service - Team Board and Agent Notes management.
"""


class TeamProtocolService:
    """Manages Team Board shared state."""

    async def get_team_board(self, conversation_id: str) -> dict:
        """Get the team board for a conversation."""
        # TODO: implement
        return {"decisions": [], "standards": [], "progress": []}

    async def add_decision(self, conversation_id: str, agent_id: str, content: str):
        """Add a team decision."""
        # TODO: implement
        pass

    async def add_note(self, conversation_id: str, from_agent: str, to_agent: str, content: str):
        """Add an agent-to-agent note."""
        # TODO: implement
        pass
