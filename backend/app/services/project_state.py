"""
Project State Service - Maintain auto-updated project state document.
"""


class ProjectStateService:
    """Maintains a summary of the project state for agent context."""

    async def get_state(self, conversation_id: str) -> dict:
        """Get current project state."""
        # TODO: implement
        return {"file_tree": [], "decisions": [], "progress": []}

    async def update_state(self, conversation_id: str, changes: dict):
        """Update project state with new changes."""
        # TODO: implement
        pass

    async def build_context_summary(self, conversation_id: str) -> str:
        """Build a text summary for agent context injection."""
        # TODO: implement
        return ""
