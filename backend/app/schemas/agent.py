"""Agent schemas"""
from pydantic import BaseModel


class AgentCreate(BaseModel):
    name: str
    avatar: str = "🤖"
    description: str = ""
    capabilities: list[str] = []
    system_instruction: str = ""
    platform_id: str


class AgentUpdate(BaseModel):
    name: str | None = None
    avatar: str | None = None
    description: str | None = None
    capabilities: list[str] | None = None
    system_instruction: str | None = None


class AgentResponse(BaseModel):
    id: str
    name: str
    avatar: str
    description: str
    capabilities: list[str]
    platform_id: str
    is_builtin: bool
    created_at: str

    class Config:
        from_attributes = True
