"""
Preview Service - Static file hosting for iframe previews.
"""


class PreviewService:
    """Hosts project files for preview in the frontend."""

    async def get_preview_url(self, conversation_id: str, file_path: str) -> str:
        """Generate a preview URL for a file."""
        # TODO: implement
        return f"/preview/{conversation_id}/{file_path}"

    async def serve_file(self, conversation_id: str, file_path: str) -> bytes:
        """Read and return file content for preview."""
        # TODO: implement
        return b""
