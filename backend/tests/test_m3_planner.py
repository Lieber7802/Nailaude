from dataclasses import dataclass

import pytest

from app.services.orchestrator_planner import OrchestratorPlanner, PlannerFailure


def task(task_id: str, agent_id: str = "agent-1") -> dict:
    return {
        "id": task_id,
        "title": task_id,
        "agentId": agent_id,
        "agentName": "Agent",
        "objective": "Do work",
        "instruction": "Do work",
        "acceptanceCriteria": ["Done"],
        "constraints": [],
        "accessMode": "read",
        "dependsOn": [],
        "priority": 50,
        "riskHints": {},
    }


@dataclass
class FakeResult:
    content: dict


class FakeClient:
    def __init__(self, outputs: list[dict]):
        self.outputs = outputs
        self.calls = 0

    async def request_json(self, messages):
        output = self.outputs[self.calls]
        self.calls += 1
        return FakeResult(output)


@pytest.mark.asyncio
async def test_planner_replans_once_after_invalid_plan():
    client = FakeClient(
        [
            {"status": "ready", "tasks": [task("one", "outside")]},
            {"status": "ready", "reasoningSummary": "fixed", "tasks": [task("one")]},
        ]
    )

    result = await OrchestratorPlanner(client).plan({"userRequest": "build"}, participant_ids={"agent-1"})

    assert result.status == "ready"
    assert client.calls == 2


@pytest.mark.asyncio
async def test_planner_normalizes_model_status_and_access_mode_casing():
    client = FakeClient(
        [
            {
                "status": "Ready",
                "reasoningSummary": "normalized",
                "tasks": [{**task("one"), "accessMode": "Write"}],
            },
        ]
    )

    result = await OrchestratorPlanner(client).plan({"userRequest": "build"}, participant_ids={"agent-1"})

    assert result.status == "ready"
    assert result.tasks[0].access_mode == "write"


@pytest.mark.asyncio
async def test_planner_normalizes_common_loose_task_fields():
    client = FakeClient(
        [
            {
                "status": "Ready",
                "reasoningSummary": "normalized",
                "tasks": [
                    {
                        "id": "one",
                        "agent": "agent-1",
                        "instructions": ["Create output.txt"],
                        "acceptanceCriteria": "output.txt exists",
                        "dependencies": [],
                    }
                ],
            },
        ]
    )

    result = await OrchestratorPlanner(client).plan(
        {"userRequest": "创建 output.txt"}, participant_ids={"agent-1"}
    )

    assert result.status == "ready"
    assert result.tasks[0].agent_id == "agent-1"
    assert result.tasks[0].title == "one"
    assert result.tasks[0].instruction == "Create output.txt"
    assert result.tasks[0].acceptance_criteria == ["output.txt exists"]
    assert result.tasks[0].access_mode == "write"


@pytest.mark.asyncio
async def test_planner_treats_task_only_output_as_ready():
    client = FakeClient(
        [
            {
                "tasks": [
                    {
                        "id": "one",
                        "agentId": "agent-1",
                        "instruction": "Create output.txt",
                        "readWriteAccess": "write",
                        "acceptanceCriteria": ["output.txt exists"],
                    }
                ],
            },
        ]
    )

    result = await OrchestratorPlanner(client).plan(
        {"userRequest": "创建 output.txt"}, participant_ids={"agent-1"}
    )

    assert result.status == "ready"
    assert result.tasks[0].access_mode == "write"


@pytest.mark.asyncio
async def test_planner_normalizes_nested_plan_output():
    client = FakeClient(
        [
            {
                "plan": {
                    "tasks": [
                        {
                            "id": "one",
                            "description": "创建 output.txt",
                            "agentId": "agent-1",
                            "writeResources": ["output.txt"],
                            "acceptanceCriteria": "output.txt exists",
                        }
                    ],
                    "dependencies": [],
                },
            },
        ]
    )

    result = await OrchestratorPlanner(client).plan(
        {"userRequest": "创建 output.txt"}, participant_ids={"agent-1"}
    )

    assert result.status == "ready"
    assert result.tasks[0].instruction == "创建 output.txt"
    assert result.tasks[0].access_mode == "write"


@pytest.mark.asyncio
async def test_planner_stops_after_second_invalid_plan():
    client = FakeClient(
        [
            {"status": "ready", "tasks": [task("one", "outside")]},
            {"status": "ready", "tasks": [task("two", "outside")]},
        ]
    )

    with pytest.raises(PlannerFailure, match="invalid after replanning"):
        await OrchestratorPlanner(client).plan({"userRequest": "build"}, participant_ids={"agent-1"})
