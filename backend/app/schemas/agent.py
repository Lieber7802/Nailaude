"""Agent schemas"""
from pydantic import BaseModel, ConfigDict, Field


class AgentCreate(BaseModel):
    name: str
    avatar: str = "🤖"
    description: str = ""
    capabilities: list[str] = Field(default_factory=list)
    system_instruction: str = Field(default="", alias="systemInstruction")
    platform_id: str = Field(default="mock", alias="platformId")

    model_config = ConfigDict(populate_by_name=True)


class AgentUpdate(BaseModel):
    name: str | None = None
    avatar: str | None = None
    description: str | None = None
    capabilities: list[str] | None = None
    system_instruction: str | None = Field(default=None, alias="systemInstruction")
    platform_id: str | None = Field(default=None, alias="platformId")

    model_config = ConfigDict(populate_by_name=True)


class AgentResponse(BaseModel):
    id: str
    name: str
    avatar: str
    description: str
    capabilities: list[str]
    platform_id: str
    is_builtin: bool
    created_at: str

    model_config = ConfigDict(from_attributes=True)
