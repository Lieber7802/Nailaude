"""Atomic Team Note records used for cross-agent handoff."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TeamNote(Base):
    __tablename__ = "team_notes"
    __table_args__ = (UniqueConstraint("conversation_id", "fingerprint", name="uq_team_notes_conversation_fingerprint"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), nullable=False)
    source_task_id: Mapped[str] = mapped_column(String(100), nullable=False)
    from_agent_id: Mapped[str] = mapped_column(String(36), nullable=False)
    from_agent_name: Mapped[str] = mapped_column(String(100), nullable=False)
    to_type: Mapped[str] = mapped_column(String(20), default="all")
    to_agent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    note_type: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    related_files: Mapped[list] = mapped_column(JSON, default=list)
    related_task_ids: Mapped[list] = mapped_column(JSON, default=list)
    resolves_note_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    injection_count: Mapped[int] = mapped_column(Integer, default=0)
    last_injected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
