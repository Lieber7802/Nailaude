"""Workspace fact snapshot used by Planner and handoff."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ProjectState(Base):
    __tablename__ = "project_states"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), unique=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    workspace: Mapped[dict] = mapped_column(JSON, default=dict)
    tech_stack: Mapped[list] = mapped_column(JSON, default=list)
    file_tree: Mapped[dict] = mapped_column(
        JSON, default=lambda: {"totalFiles": 0, "paths": [], "truncated": False}
    )
    git: Mapped[dict] = mapped_column(JSON, default=lambda: {"isRepository": False, "dirty": False, "recentCommits": []})
    progress_summary: Mapped[str] = mapped_column(Text, default="")
    recent_changes: Mapped[list] = mapped_column(JSON, default=list)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
