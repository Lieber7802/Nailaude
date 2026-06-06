"""
Preview Service - Static file hosting for iframe previews.
"""
import mimetypes
import re
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.services.workspace_paths import resolve_workspace_path


PREVIEW_CSP = "default-src 'self' 'unsafe-inline' data: blob:; script-src 'self' 'unsafe-inline'; frame-ancestors 'self'"


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

    async def file_response(self, db: AsyncSession, conversation_id: str, file_path: str) -> FileResponse | Response:
        """Return a raw static file response for the preview route."""
        conversation = await db.get(Conversation, conversation_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        path = self._resolve_preview_path(conversation.work_dir, file_path)
        if not path.is_file():
            raise HTTPException(status_code=404, detail="Preview file not found")

        media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        headers = {
            "Content-Security-Policy": PREVIEW_CSP,
            "X-Content-Type-Options": "nosniff",
        }
        if media_type == "text/html":
            html = path.read_text(encoding="utf-8", errors="replace")
            return Response(
                self._rewrite_html_asset_urls(html, conversation_id, file_path),
                media_type=media_type,
                headers=headers,
            )

        return FileResponse(
            path,
            media_type=media_type,
            headers=headers,
        )

    def _resolve_preview_path(self, work_dir: str, file_path: str) -> Path:
        root = resolve_workspace_path(work_dir)
        requested = (root / file_path.replace("\\", "/").lstrip("/")).resolve()
        if not requested.is_relative_to(root):
            raise HTTPException(status_code=403, detail="Preview path escapes the workspace")
        return requested

    def _rewrite_html_asset_urls(self, html: str, conversation_id: str, file_path: str) -> str:
        safe_file_path = file_path.replace("\\", "/").lstrip("/")
        preview_dir = str(Path(safe_file_path).parent).replace("\\", "/")
        preview_prefix = f"/preview/{conversation_id}"
        if preview_dir and preview_dir != ".":
            preview_prefix = f"{preview_prefix}/{preview_dir}"

        def replace(match: re.Match[str]) -> str:
            attr = match.group("attr")
            quote = match.group("quote")
            url = match.group("url")
            if url.startswith("/preview/"):
                return match.group(0)
            return f"{attr}{quote}{preview_prefix}{url}{quote}"

        return re.sub(
            r"(?P<attr>\b(?:src|href)=)(?P<quote>['\"])(?P<url>/(?!/)[^'\"]+)(?P=quote)",
            replace,
            html,
        )
