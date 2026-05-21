"""Artifact model"""
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id: Mapped[str] = mapped_column(String(36), ForeignKey("messages.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # code | webpage | diff | document | file | log
    title: Mapped[str] = mapped_column(String(200), default="")
    files: Mapped[list] = mapped_column(JSON, default=list)  # [{name, content, language}]
    diff_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    content: Mapped[str] = mapped_column(Text, default="")
    version: Mapped[int] = mapped_column(Integer, default=1)
    previous_version_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    preview_url: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
