import pytest
from pydantic import ValidationError

from app.schemas.orchestrator import (
    CapabilityGapPlannerResult,
    CannotPlanPlannerResult,
    NeedsClarificationPlannerResult,
    ReadyPlannerResult,
)


def ready_payload() -> dict:
    return {
        "status": "ready",
        "reasoningSummary": "Implementation and review can run independently.",
        "tasks": [
            {
                "id": "task-1",
                "title": "Implement login",
                "agentId": "agent-1",
                "agentName": "Builder",
                "objective": "Create the login page.",
                "instruction": "Implement the login form.",
                "acceptanceCriteria": ["Shows loading state"],
                "constraints": ["Do not add dependencies"],
                "accessMode": "write",
                "dependsOn": [],
                "priority": 80,
                "riskHints": {
                    "mayDeleteOrRenameFiles": False,
                    "mayTouchConfigFiles": False,
                    "estimatedFilesTouched": 2,
                },
            }
        ],
    }


def test_ready_planner_result_parses_task_contract():
    result = ReadyPlannerResult.model_validate(ready_payload())

    assert result.status == "ready"
    assert result.tasks[0].depends_on == []
    assert result.tasks[0].access_mode == "write"


def test_clarification_planner_result_requires_recommended_option():
    result = NeedsClarificationPlannerResult.model_validate(
        {
            "status": "needs_clarification",
            "questions": [
                {
                    "id": "storage",
                    "question": "Where should state be saved?",
                    "reason": "This affects refresh behavior.",
                    "options": [
                        {"id": "local", "label": "localStorage", "recommended": True},
                        {"id": "memory", "label": "Memory only", "recommended": False},
                    ],
                    "allowCustomInput": True,
                }
            ],
        }
    )

    assert result.questions[0].options[0].recommended is True


def test_capability_gap_planner_result_parses_recommendations():
    result = CapabilityGapPlannerResult.model_validate(
        {
            "status": "capability_gap",
            "missingCapabilities": ["security review"],
            "recommendedAgents": [{"agentId": "agent-security", "reason": "Security specialist"}],
        }
    )

    assert result.recommended_agents[0].agent_id == "agent-security"


def test_cannot_plan_planner_result_parses_reason():
    result = CannotPlanPlannerResult.model_validate(
        {"status": "cannot_plan", "reason": "Outside workspace", "recoverable": True}
    )

    assert result.recoverable is True


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("dependsOn", None),
        ("accessMode", "admin"),
        ("acceptanceCriteria", []),
    ],
)
def test_ready_planner_result_rejects_invalid_task_contract(field: str, value):
    payload = ready_payload()
    payload["tasks"][0][field] = value

    with pytest.raises(ValidationError):
        ReadyPlannerResult.model_validate(payload)


def test_clarification_rejects_options_without_recommended_choice():
    with pytest.raises(ValidationError):
        NeedsClarificationPlannerResult.model_validate(
            {
                "status": "needs_clarification",
                "questions": [
                    {
                        "id": "storage",
                        "question": "Where should state be saved?",
                        "reason": "This affects refresh behavior.",
                        "options": [{"id": "local", "label": "localStorage", "recommended": False}],
                        "allowCustomInput": True,
                    }
                ],
            }
        )
