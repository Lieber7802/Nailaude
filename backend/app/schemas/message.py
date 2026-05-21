"""Message schemas"""
from pydantic import BaseModel


class MentionSchema(BaseModel):
    agent_id: str
    agent_name: str


class MessageCreate(BaseModel):
    content: str
    mentions: list[MentionSchema] = []
    parent_message_id: str | None = None


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    agent_id: str | None = None
    content: str
    content_type: str
    mentions: list[MentionSchema]
    created_at: str

    class Config:
        from_attributes = True
