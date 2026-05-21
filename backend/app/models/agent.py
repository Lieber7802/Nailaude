"""Agent and AgentPlatform models"""
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AgentPlatform(Base):
    __tablename__ = "agent_platforms"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # "mock" | "opencode" | "codex" | "llm_provider"
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    binary_path: Mapped[str] = mapped_column(String(500), default="")
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="available")  # available | not_installed | error
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar: Mapped[str] = mapped_column(String(50), default="🤖")
    description: Mapped[str] = mapped_column(Text, default="")
    capabilities: Mapped[list] = mapped_column(JSON, default=list)
    system_instruction: Mapped[str] = mapped_column(Text, default="")
    platform_id: Mapped[str] = mapped_column(String(50), ForeignKey("agent_platforms.id"), nullable=False)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
