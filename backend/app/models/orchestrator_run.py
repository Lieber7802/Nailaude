"""Persistent Orchestrator run state and latest full snapshot."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class OrchestratorRun(Base):
    __tablename__ = "orchestrator_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), nullable=False)
    user_message_id: Mapped[str] = mapped_column(String(36), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="queued")
    sequence: Mapped[int] = mapped_column(Integer, default=0)
    reasoning_summary: Mapped[str] = mapped_column(Text, default="")
    tasks: Mapped[list] = mapped_column(JSON, default=list)
    batches: Mapped[list] = mapped_column(JSON, default=list)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    latest_snapshot: Mapped[dict] = mapped_column(JSON, default=dict)
    clarification_answers: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
