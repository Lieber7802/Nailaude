"""Conversation schemas"""
from pathlib import Path
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


PROJECT_ROOT = Path(__file__).resolve().parents[3]
WORKSPACE_ROOT = (PROJECT_ROOT / "workspaces").resolve(strict=False)
WINDOWS_WORKSPACE_PATTERN = re.compile(r"^[A-Za-z]:[/\\].*[/\\]workspaces[/\\].+")


def validate_work_dir(value: str | None) -> str | None:
    if value is None or value == "":
        return value

    if WINDOWS_WORKSPACE_PATTERN.match(value):
        return value

    raw_path = Path(value).expanduser()
    candidate = raw_path if raw_path.is_absolute() else PROJECT_ROOT / raw_path
    resolved = candidate.resolve(strict=False)
    try:
        resolved.relative_to(WORKSPACE_ROOT)
    except ValueError as exc:
        raise ValueError("workDir must stay under the project workspaces directory") from exc
    return value


class ConversationCreate(BaseModel):
    title: str = "新对话"
    type: Literal["single", "group"] = "single"
    work_dir: str = Field(default="", alias="workDir")
    participant_ids: list[str] = Field(default_factory=list, alias="participantIds")

    @field_validator("work_dir")
    @classmethod
    def work_dir_must_stay_in_workspaces(cls, value: str) -> str:
        return validate_work_dir(value) or ""

    @field_validator("participant_ids")
    @classmethod
    def participants_must_not_be_empty(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("participantIds must include at least one agent")
        return value

    model_config = ConfigDict(populate_by_name=True)


class ConversationUpdate(BaseModel):
    title: str | None = None
    work_dir: str | None = Field(default=None, alias="workDir")
    participant_ids: list[str] | None = Field(default=None, alias="participantIds")

    @field_validator("work_dir")
    @classmethod
    def work_dir_must_stay_in_workspaces(cls, value: str | None) -> str | None:
        return validate_work_dir(value)

    @field_validator("participant_ids")
    @classmethod
    def participants_must_not_be_empty(cls, value: list[str] | None) -> list[str] | None:
        if value is not None and not value:
            raise ValueError("participantIds must include at least one agent")
        return value

    model_config = ConfigDict(populate_by_name=True)


class ConversationResponse(BaseModel):
    id: str
    title: str
    type: str
    work_dir: str
    participant_ids: list[str]
    created_at: str
    updated_at: str

    model_config = ConfigDict(from_attributes=True)
