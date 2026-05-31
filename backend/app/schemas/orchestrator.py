"""Pydantic contracts for M3 orchestrator planning and collaboration state."""
from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


def to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class RiskHints(CamelModel):
    may_delete_or_rename_files: bool = False
    may_touch_config_files: bool = False
    estimated_files_touched: int = Field(default=0, ge=0)


class PlannedTask(CamelModel):
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    agent_name: str = ""
    objective: str = Field(min_length=1)
    instruction: str = Field(min_length=1)
    acceptance_criteria: list[str] = Field(min_length=1)
    constraints: list[str] = Field(default_factory=list)
    access_mode: Literal["read", "write"]
    depends_on: list[str] = Field(default_factory=list)
    priority: int = Field(default=50, ge=0, le=100)
    risk_hints: RiskHints = Field(default_factory=RiskHints)

    @model_validator(mode="after")
    def require_non_empty_acceptance_criteria(self):
        if any(not criterion.strip() for criterion in self.acceptance_criteria):
            raise ValueError("acceptance criteria must not be blank")
        return self


class PlannerOption(CamelModel):
    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    recommended: bool = False


class PlanningQuestion(CamelModel):
    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    options: list[PlannerOption] = Field(default_factory=list)
    allow_custom_input: bool = True

    @model_validator(mode="after")
    def require_one_recommended_option(self):
        if self.options and sum(option.recommended for option in self.options) != 1:
            raise ValueError("questions with options require exactly one recommended option")
        return self


class RecommendedAgent(CamelModel):
    agent_id: str = Field(min_length=1)
    reason: str = Field(min_length=1)


class ReadyPlannerResult(CamelModel):
    status: Literal["ready"]
    reasoning_summary: str = ""
    tasks: list[PlannedTask] = Field(min_length=1, max_length=16)


class NeedsClarificationPlannerResult(CamelModel):
    status: Literal["needs_clarification"]
    questions: list[PlanningQuestion] = Field(min_length=1, max_length=10)


class CapabilityGapPlannerResult(CamelModel):
    status: Literal["capability_gap"]
    missing_capabilities: list[str] = Field(min_length=1)
    recommended_agents: list[RecommendedAgent] = Field(min_length=1)


class CannotPlanPlannerResult(CamelModel):
    status: Literal["cannot_plan"]
    reason: str = Field(min_length=1)
    recoverable: bool = True


PlannerResult = Annotated[
    ReadyPlannerResult | NeedsClarificationPlannerResult | CapabilityGapPlannerResult | CannotPlanPlannerResult,
    Field(discriminator="status"),
]


class PlannerContext(CamelModel):
    user_request: str
    mentions: list[dict] = Field(default_factory=list)
    clarification_answers: list[dict] = Field(default_factory=list)
    participants: list[dict] = Field(default_factory=list)
    available_agent_catalog: list[dict] = Field(default_factory=list)
    project_planning_summary: dict = Field(default_factory=dict)
    team_board_summary: dict = Field(default_factory=dict)
    recent_conversation_summary: list[dict] = Field(default_factory=list)
    file_tree_summary: list[str] = Field(default_factory=list)
    previous_validation_errors: list[str] = Field(default_factory=list)


class WorkspaceAccess(CamelModel):
    path: str
    access_mode: Literal["read", "write"]
    snapshot_id: str


class HandoffManifest(CamelModel):
    estimated_tokens: int = 0
    warnings: list[str] = Field(default_factory=list)
    omitted_items: list[str] = Field(default_factory=list)


class AgentHandoffEnvelope(CamelModel):
    run_id: str
    task_id: str
    batch_id: str
    workspace: WorkspaceAccess
    task: PlannedTask
    collaboration: dict = Field(default_factory=dict)
    navigation_hints: dict = Field(default_factory=dict)
    manifest: HandoffManifest = Field(default_factory=HandoffManifest)


class TaskResult(CamelModel):
    status: Literal["success", "failed", "partial"]
    summary: str = ""
    files_read: list[str] = Field(default_factory=list)
    files_changed: list[str] = Field(default_factory=list)
    files_created: list[str] = Field(default_factory=list)
    files_deleted: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    team_notes: list[dict] = Field(default_factory=list)
    error: str | None = None
