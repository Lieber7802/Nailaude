import pytest

from app.schemas.orchestrator import ReadyPlannerResult
from app.services.orchestrator_validator import PlanValidationError, PlanValidator


def task(task_id: str, *, agent_id: str = "agent-1", depends_on=None, access_mode: str = "read") -> dict:
    return {
        "id": task_id,
        "title": task_id,
        "agentId": agent_id,
        "agentName": "Agent",
        "objective": "Do work",
        "instruction": "Do work",
        "acceptanceCriteria": ["Done"],
        "constraints": [],
        "accessMode": access_mode,
        "dependsOn": depends_on or [],
        "priority": 50,
        "riskHints": {
            "mayDeleteOrRenameFiles": False,
            "mayTouchConfigFiles": False,
            "estimatedFilesTouched": 0,
        },
    }


@pytest.mark.parametrize(
    "tasks",
    [
        [task("one"), task("one")],
        [task("one", depends_on=["missing"])],
        [task("one", depends_on=["one"])],
        [task("one", depends_on=["two"]), task("two", depends_on=["one"])],
        [task("one", agent_id="outside")],
    ],
)
def test_validator_rejects_invalid_graphs_and_agents(tasks):
    plan = ReadyPlannerResult.model_validate({"status": "ready", "tasks": tasks})

    with pytest.raises(PlanValidationError):
        PlanValidator().validate(plan, participant_ids={"agent-1"})


def test_validator_rejects_nonexistent_agent_id():
    tasks = [task("one", agent_id="agent-1")]
    plan = ReadyPlannerResult.model_validate({"status": "ready", "tasks": tasks})

    with pytest.raises(PlanValidationError, match="does not exist"):
        PlanValidator().validate(plan, participant_ids={"agent-1"}, available_agent_ids={"agent-1", "agent-2"})


def test_validator_accepts_plan_when_available_agent_ids_not_provided():
    tasks = [task("one", agent_id="agent-1")]
    plan = ReadyPlannerResult.model_validate({"status": "ready", "tasks": tasks})

    PlanValidator().validate(plan, participant_ids={"agent-1"})


def test_validator_rejects_agent_not_in_available_ids_even_if_participant():
    tasks = [task("one", agent_id="agent-1")]
    plan = ReadyPlannerResult.model_validate({"status": "ready", "tasks": tasks})

    with pytest.raises(PlanValidationError, match="does not exist"):
        PlanValidator().validate(plan, participant_ids={"agent-1"}, available_agent_ids={"agent-2"})
