"""Conversation-level Team Board snapshot."""
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TeamBoard(Base):
    __tablename__ = "team_boards"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id"), unique=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    team_members: Mapped[list] = mapped_column(JSON, default=list)
    decisions: Mapped[list] = mapped_column(JSON, default=list)
    code_standards: Mapped[list] = mapped_column(JSON, default=list)
    open_questions: Mapped[list] = mapped_column(JSON, default=list)
    progress: Mapped[dict] = mapped_column(
        JSON,
        default=lambda: {
            "completedTaskIds": [],
            "activeTaskIds": [],
            "blockedTaskIds": [],
            "pendingTaskIds": [],
            "currentFocus": "",
        },
    )
    recent_notes: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
