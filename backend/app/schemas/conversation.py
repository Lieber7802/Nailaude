"""Conversation schemas"""
from pydantic import BaseModel


class ConversationCreate(BaseModel):
    title: str = "新对话"
    type: str = "single"  # single | group
    work_dir: str = ""
    participant_ids: list[str] = []


class ConversationUpdate(BaseModel):
    title: str | None = None
    work_dir: str | None = None
    participant_ids: list[str] | None = None


class ConversationResponse(BaseModel):
    id: str
    title: str
    type: str
    work_dir: str
    participant_ids: list[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
