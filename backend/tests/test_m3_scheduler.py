from app.schemas.orchestrator import ReadyPlannerResult
from app.services.orchestrator_scheduler import OrchestratorScheduler
from tests.test_m3_validator import task


def test_scheduler_allows_one_write_and_two_reads_in_same_batch():
    plan = ReadyPlannerResult.model_validate(
        {
            "status": "ready",
            "tasks": [
                task("write", access_mode="write"),
                task("read-1", agent_id="agent-2"),
                task("read-2", agent_id="agent-3"),
            ],
        }
    )

    batches = OrchestratorScheduler().schedule(plan.tasks)

    assert batches[0]["taskIds"] == ["write", "read-1", "read-2"]


def test_scheduler_separates_independent_writes_and_honors_dependencies():
    plan = ReadyPlannerResult.model_validate(
        {
            "status": "ready",
            "tasks": [
                task("write-1", access_mode="write"),
                task("write-2", access_mode="write"),
                task("review", depends_on=["write-2"]),
            ],
        }
    )

    batches = OrchestratorScheduler().schedule(plan.tasks)

    assert [batch["taskIds"] for batch in batches] == [["write-1"], ["write-2"], ["review"]]
