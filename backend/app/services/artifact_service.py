"""
Artifact Service - Parse agent outputs into displayable artifacts.
"""
import difflib
import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.base import AgentEvent
from app.models.artifact import Artifact
from app.services.preview_service import PreviewService


LANGUAGE_BY_SUFFIX = {
    ".css": "css",
    ".html": "html",
    ".js": "javascript",
    ".json": "json",
    ".jsx": "jsx",
    ".md": "markdown",
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".txt": "text",
}
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def infer_language(file_path: str) -> str:
    """Infer editor language from a file name."""
    return LANGUAGE_BY_SUFFIX.get(Path(file_path).suffix.lower(), "text")


def build_diff_data(file_path: str, old_content: str, new_content: str) -> dict:
    """Build shared DiffData from two text snapshots."""
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()
    diff_lines = list(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="",
        )
    )
    hunk_lines = [line for line in diff_lines if not line.startswith("--- ") and not line.startswith("+++ ")]
    additions = sum(1 for line in hunk_lines if line.startswith("+") and not line.startswith("+++"))
    deletions = sum(1 for line in hunk_lines if line.startswith("-") and not line.startswith("---"))
    return {
        "file": file_path,
        "hunks": [
            {
                "oldStart": 1,
                "oldLines": len(old_lines),
                "newStart": 1,
                "newLines": len(new_lines),
                "content": "\n".join(hunk_lines),
            }
        ],
        "additions": additions,
        "deletions": deletions,
        "oldContent": old_content,
        "newContent": new_content,
    }


class ArtifactService:
    """Handles artifact creation and management."""

    def __init__(self, preview_service: PreviewService | None = None):
        self.preview_service = preview_service or PreviewService()

    async def create_artifact(
        self,
        db: AsyncSession,
        message_id: str,
        artifact_type: str,
        *,
        title: str = "",
        files: list[dict] | None = None,
        diff_data: dict | None = None,
        preview_url: str | None = None,
        previous_version_id: str | None = None,
        version: int = 1,
    ) -> Artifact:
        """Create and persist a new artifact from agent output."""
        artifact = Artifact(
            message_id=message_id,
            type=artifact_type,
            title=title,
            files=files or [],
            diff_data=diff_data,
            version=version,
            previous_version_id=previous_version_id,
            preview_url=preview_url or "",
        )
        db.add(artifact)
        await db.commit()
        await db.refresh(artifact)
        return artifact

    async def create_from_agent_event(
        self,
        db: AsyncSession,
        *,
        message_id: str,
        conversation_id: str,
        work_dir: str,
        event: AgentEvent,
    ) -> list[Artifact]:
        """Convert file AgentEvents into persisted artifacts."""
        if event.type not in {"file_created", "file_modified"}:
            return []

        metadata = event.metadata or {}
        files = self._normalize_files(metadata.get("files") or [], fallback_name=event.content)
        files_written = False
        if files:
            files_written = self._write_files(work_dir, files)

        primary_file = files[0] if files else {"name": event.content or "artifact.txt", "content": "", "language": "text"}
        artifact_type = str(metadata.get("type") or self._artifact_type_for_file(primary_file))
        preview_url = metadata.get("previewUrl")
        if preview_url is None and artifact_type == "webpage" and files_written:
            preview_url = await self.preview_service.get_preview_url(conversation_id, primary_file["name"])

        artifacts = [
            await self.create_artifact(
                db,
                message_id,
                artifact_type,
                title=str(metadata.get("title") or primary_file["name"]),
                files=files,
                preview_url=preview_url,
            )
        ]

        if event.type == "file_modified":
            old_content = str(metadata.get("oldContent") or "")
            new_content = str(metadata.get("newContent") or primary_file.get("content") or "")
            diff_data = metadata.get("diffData") or build_diff_data(primary_file["name"], old_content, new_content)
            artifacts.append(
                await self.create_artifact(
                    db,
                    message_id,
                    "diff",
                    title=f"{primary_file['name']} 变更",
                    files=[],
                    diff_data=diff_data,
                )
            )

        return artifacts

    async def get_artifacts(self, db: AsyncSession, message_id: str) -> list[Artifact]:
        """Get all artifacts for a message."""
        result = await db.scalars(
            select(Artifact).where(Artifact.message_id == message_id).order_by(Artifact.created_at.asc())
        )
        return list(result.all())

    async def parse_code_blocks(self, content: str) -> list:
        """Extract fenced code blocks from agent text output."""
        blocks = []
        for index, match in enumerate(re.finditer(r"```(\w+)?\n(.*?)```", content, flags=re.DOTALL), start=1):
            language = match.group(1) or "text"
            extension = "txt" if language == "text" else language
            blocks.append(
                {
                    "name": f"snippet-{index}.{extension}",
                    "content": match.group(2).strip(),
                    "language": language,
                }
            )
        return blocks

    def _normalize_files(self, files: list[dict], fallback_name: str = "") -> list[dict]:
        normalized = []
        for file in files:
            name = str(file.get("name") or fallback_name or "artifact.txt").replace("\\", "/")
            normalized.append(
                {
                    "name": name,
                    "content": str(file.get("content") or ""),
                    "language": str(file.get("language") or infer_language(name)),
                }
            )
        return normalized

    def _artifact_type_for_file(self, file: dict) -> str:
        language = str(file.get("language") or "").lower()
        name = str(file.get("name") or "").lower()
        if language == "html" or name.endswith(".html") or name.endswith(".htm"):
            return "webpage"
        return "code"

    def _write_files(self, work_dir: str, files: list[dict]) -> bool:
        root = resolve_work_dir(work_dir)
        try:
            root.mkdir(parents=True, exist_ok=True)
            for file in files:
                destination = (root / file["name"]).resolve()
                if not destination.is_relative_to(root):
                    raise ValueError("Artifact file path escapes the workspace")
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(file["content"], encoding="utf-8")
        except OSError:
            return False
        return True


def resolve_work_dir(work_dir: str) -> Path:
    path = Path(work_dir).expanduser()
    return path.resolve() if path.is_absolute() else (PROJECT_ROOT / path).resolve()
