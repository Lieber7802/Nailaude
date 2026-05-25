"""Message schemas"""
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MentionSchema(BaseModel):
    agent_id: str = Field(alias="agentId")
    agent_name: str = Field(alias="agentName")

    model_config = ConfigDict(populate_by_name=True)


class MessageCreate(BaseModel):
    content: str
    mentions: list[MentionSchema] = Field(default_factory=list)
    parent_message_id: str | None = Field(default=None, alias="parentMessageId")

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("content must not be empty")
        return value

    model_config = ConfigDict(populate_by_name=True)


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    agent_id: str | None = None
    content: str
    content_type: str
    mentions: list[MentionSchema]
    created_at: str

    model_config = ConfigDict(from_attributes=True)
