"""Conversation model"""
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200), default="新对话")
    type: Mapped[str] = mapped_column(String(10), default="single")  # single | group
    work_dir: Mapped[str] = mapped_column(String(500), default="")
    participant_ids: Mapped[list] = mapped_column(JSON, default=list)  # Agent ID list
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
