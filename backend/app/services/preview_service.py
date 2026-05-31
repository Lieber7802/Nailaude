"""
Preview Service - Static file hosting for iframe previews.
"""
import mimetypes
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation


PREVIEW_CSP = "default-src 'self' 'unsafe-inline' data: blob:; script-src 'self' 'unsafe-inline'; frame-ancestors 'self'"
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class PreviewService:
    """Hosts project files for preview in the frontend."""

    async def get_preview_url(self, conversation_id: str, file_path: str) -> str:
        """Generate a preview URL for a file."""
        safe_path = file_path.replace("\\", "/").lstrip("/")
        return f"/preview/{conversation_id}/{safe_path}"

    async def serve_file(self, conversation_id: str, file_path: str, work_dir: str | None = None) -> bytes:
        """Read and return file content for preview."""
        if not work_dir:
            raise FileNotFoundError(f"No preview root for conversation {conversation_id}")
        path = self._resolve_preview_path(work_dir, file_path)
        return path.read_bytes()

    async def file_response(self, db: AsyncSession, conversation_id: str, file_path: str) -> FileResponse:
        """Return a raw static file response for the preview route."""
        conversation = await db.get(Conversation, conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        path = self._resolve_preview_path(conversation.work_dir, file_path)
        if not path.is_file():
            raise HTTPException(status_code=404, detail="Preview file not found")

        media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return FileResponse(
            path,
            media_type=media_type,
            headers={
                "Content-Security-Policy": PREVIEW_CSP,
                "X-Content-Type-Options": "nosniff",
            },
        )

    def _resolve_preview_path(self, work_dir: str, file_path: str) -> Path:
        work_dir_path = Path(work_dir).expanduser()
        root = work_dir_path.resolve() if work_dir_path.is_absolute() else (PROJECT_ROOT / work_dir_path).resolve()
        requested = (root / file_path.replace("\\", "/").lstrip("/")).resolve()
        if not requested.is_relative_to(root):
            raise HTTPException(status_code=403, detail="Preview path escapes the workspace")
        return requested
