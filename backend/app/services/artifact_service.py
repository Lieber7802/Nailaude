"""
Artifact Service - Parse agent outputs into displayable artifacts.
"""


class ArtifactService:
    """Handles artifact creation and management."""

    async def create_artifact(self, message_id: str, artifact_type: str, **kwargs):
        """Create a new artifact from agent output."""
        # TODO: implement
        pass

    async def get_artifacts(self, message_id: str) -> list:
        """Get all artifacts for a message."""
        # TODO: implement
        return []

    async def parse_code_blocks(self, content: str) -> list:
        """Extract code blocks from agent text output."""
        # TODO: implement
        return []
