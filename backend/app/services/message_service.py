"""
Message Service - Message CRUD and context building.
"""


class MessageService:
    """Handles message persistence and retrieval."""

    async def create_message(self, conversation_id: str, role: str, content: str, **kwargs):
        """Create and persist a new message."""
        # TODO: implement
        pass

    async def get_messages(self, conversation_id: str, limit: int = 50, offset: int = 0):
        """Get messages for a conversation with pagination."""
        # TODO: implement
        return []

    async def build_context(self, conversation_id: str, max_messages: int = 20) -> list:
        """Build context from recent messages for agent dispatch."""
        # TODO: implement
        return []
