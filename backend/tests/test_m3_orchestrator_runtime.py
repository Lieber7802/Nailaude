import asyncio

import pytest

from app.services.orchestrator_queue import OrchestratorQueue, QueueFullError
from app.services.orchestrator_runtime import OrchestratorRuntime


def task(task_id: str, *, access_mode: str = "read", agent_id: str = "agent-1", depends_on=None) -> dict:
    return {
        "id": task_id,
        "title": task_id,
        "agentId": agent_id,
        "agentName": agent_id,
        "objective": "Do work",
        "instruction": "Do work",
        "acceptanceCriteria": ["Done"],
        "constraints": [],
        "accessMode": access_mode,
        "dependsOn": depends_on or [],
        "priority": 50,
        "riskHints": {},
        "status": "pending",
    }


def test_orchestrator_queue_is_fifo_and_enforces_limit():
    queue = OrchestratorQueue(max_queued=2)
    queue.enqueue("conversation", "run-1")
    queue.enqueue("conversation", "run-2")
    with pytest.raises(QueueFullError):
        queue.enqueue("conversation", "run-3")

    assert queue.activate_next("conversation") == "run-1"
    queue.complete_current("conversation")
    assert queue.activate_next("conversation") == "run-2"


def test_orchestrator_queue_can_cancel_next_queued_run():
    queue = OrchestratorQueue(max_queued=2)
    queue.enqueue("conversation", "run-1")
    queue.enqueue("conversation", "run-2")

    assert queue.cancel_queued("conversation") == "run-1"
    assert queue.activate_next("conversation") == "run-2"


@pytest.mark.asyncio
async def test_runtime_honors_cancel_requested_before_execute_starts(tmp_path):
    executor_called = False
    snapshots = []
    runtime = OrchestratorRuntime()
    runtime.cancel("run-early")

    async def executor(planned_task, workspace):
        nonlocal executor_called
        executor_called = True
        return {"status": "success", "summary": "should not run", "teamNotes": []}

    async def emit(snapshot):
        snapshots.append(snapshot)

    snapshot = await runtime.execute(
        run_id="run-early",
        conversation_id="conversation",
        work_dir=str(tmp_path),
        tasks=[task("write", access_mode="write")],
        executor=executor,
        emit=emit,
    )

    assert executor_called is False
    assert snapshot["status"] == "cancelled"
    assert snapshots[-1]["status"] == "cancelled"
    assert snapshots[-1]["tasks"][0]["status"] == "cancelled"


@pytest.mark.asyncio
async def test_runtime_executes_parallel_batch_and_blocks_failed_dependents(tmp_path):
    active = 0
    max_active = 0

    async def executor(planned_task, workspace):
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.01)
        active -= 1
        if planned_task["id"] == "write":
            return {"status": "failed", "summary": "", "error": "boom", "teamNotes": []}
        return {"status": "success", "summary": workspace.path, "teamNotes": []}

    runtime = OrchestratorRuntime()
    snapshot = await runtime.execute(
        run_id="run-1",
        conversation_id="conversation",
        work_dir=str(tmp_path),
        tasks=[
            task("write", access_mode="write"),
            task("read", agent_id="agent-2"),
            task("blocked", agent_id="agent-3", depends_on=["write"]),
        ],
        executor=executor,
    )

    states = {item["id"]: item["status"] for item in snapshot["tasks"]}
    assert max_active == 2
    assert states == {"write": "failed", "read": "completed", "blocked": "blocked"}


@pytest.mark.asyncio
async def test_runtime_completes_with_warning_when_shared_refresh_fails(tmp_path):
    async def executor(planned_task, workspace):
        return {"status": "success", "summary": "ok", "teamNotes": []}

    async def refresh(batch_results, batch):
        raise RuntimeError("summary offline")

    snapshot = await OrchestratorRuntime().execute(
        run_id="run-1",
        conversation_id="conversation",
        work_dir=str(tmp_path),
        tasks=[task("read")],
        executor=executor,
        refresh_shared_state=refresh,
    )

    assert snapshot["status"] == "completed"
    assert "summary offline" in snapshot["warnings"][0]


@pytest.mark.asyncio
async def test_runtime_keeps_refresh_warnings_from_shared_state(tmp_path):
    async def executor(planned_task, workspace):
        return {"status": "success", "summary": "ok", "teamNotes": []}

    async def refresh(batch_results, batch):
        return {"teamBoardVersion": 2, "projectStateVersion": 3, "warnings": ["summary degraded"]}

    snapshot = await OrchestratorRuntime().execute(
        run_id="run-1",
        conversation_id="conversation",
        work_dir=str(tmp_path),
        tasks=[task("read")],
        executor=executor,
        refresh_shared_state=refresh,
    )

    assert snapshot["status"] == "completed"
    assert snapshot["teamBoardVersion"] == 2
    assert snapshot["projectStateVersion"] == 3
    assert snapshot["warnings"] == ["summary degraded"]


@pytest.mark.asyncio
async def test_runtime_passes_task_metadata_to_shared_refresh_when_executor_raises(tmp_path):
    captured_results = []

    async def executor(planned_task, workspace):
        raise RuntimeError("adapter exploded")

    async def refresh(batch_results, batch):
        captured_results.extend(batch_results)
        return {"teamBoardVersion": 1, "projectStateVersion": 1, "warnings": []}

    snapshot = await OrchestratorRuntime().execute(
        run_id="run-1",
        conversation_id="conversation",
        work_dir=str(tmp_path),
        tasks=[task("write", access_mode="write")],
        executor=executor,
        refresh_shared_state=refresh,
    )

    assert snapshot["warnings"] == []
    assert captured_results[0]["taskId"] == "write"
    assert captured_results[0]["agentId"] == "agent-1"
    assert captured_results[0]["batchId"] == "batch-1"
    assert captured_results[0]["status"] == "failed"
    assert captured_results[0]["error"] == "adapter exploded"


@pytest.mark.asyncio
async def test_runtime_cancel_marks_unstarted_tasks_cancelled(tmp_path):
    started = asyncio.Event()
    release = asyncio.Event()
    runtime = OrchestratorRuntime()

    async def executor(planned_task, workspace):
        started.set()
        await release.wait()
        return {"status": "success", "summary": "ok", "teamNotes": []}

    execution = asyncio.create_task(
        runtime.execute(
            run_id="run-1",
            conversation_id="conversation",
            work_dir=str(tmp_path),
            tasks=[task("write", access_mode="write"), task("next", depends_on=["write"])],
            executor=executor,
        )
    )
    await started.wait()
    runtime.cancel("run-1")
    release.set()
    snapshot = await execution

    assert snapshot["status"] == "cancelled"
    assert {item["id"]: item["status"] for item in snapshot["tasks"]}["next"] == "cancelled"


@pytest.mark.asyncio
async def test_runtime_cancel_stops_blocked_executor_without_manual_release(tmp_path):
    started = asyncio.Event()
    runtime = OrchestratorRuntime()

    async def executor(planned_task, workspace):
        started.set()
        await asyncio.Event().wait()

    execution = asyncio.create_task(
        runtime.execute(
            run_id="run-1",
            conversation_id="conversation",
            work_dir=str(tmp_path),
            tasks=[task("write", access_mode="write")],
            executor=executor,
        )
    )
    await started.wait()

    runtime.cancel("run-1")
    snapshot = await asyncio.wait_for(execution, timeout=0.25)

    assert snapshot["status"] == "cancelled"
    assert snapshot["tasks"][0]["status"] == "cancelled"


@pytest.mark.asyncio
async def test_runtime_allows_success_without_workspace_change(tmp_path):
    async def executor(planned_task, workspace):
        return {"status": "success", "summary": "claimed success", "teamNotes": []}

    snapshot = await OrchestratorRuntime().execute(
        run_id="run-1",
        conversation_id="conversation",
        work_dir=str(tmp_path),
        tasks=[task("write", access_mode="write")],
        executor=executor,
    )

    write_task = snapshot["tasks"][0]
    assert write_task["status"] == "completed"
    assert write_task["result"] == "claimed success"
    assert write_task["audit"]["filesChanged"] == []


@pytest.mark.asyncio
async def test_runtime_uses_real_workspace_for_read_metadata_tasks(tmp_path):
    paths = []

    async def executor(planned_task, workspace):
        paths.append(workspace.path)
        return {"status": "success", "summary": "ok", "teamNotes": []}

    await OrchestratorRuntime().execute(
        run_id="run-1",
        conversation_id="conversation",
        work_dir=str(tmp_path),
        tasks=[task("review", access_mode="read")],
        executor=executor,
    )

    assert paths == [str(tmp_path)]


@pytest.mark.asyncio
async def test_runtime_allows_write_workspace_review_without_file_changes_when_summary_exists(tmp_path):
    async def executor(planned_task, workspace):
        return {"status": "success", "summary": "Review complete: no blocking issues.", "teamNotes": []}

    review_task = task("review", access_mode="write")
    review_task.update(
        {
            "title": "Review index.html",
            "objective": "Review the generated page",
            "instruction": "Review index.html and summarize quality issues without modifying files.",
            "acceptanceCriteria": ["Return review findings"],
        }
    )

    snapshot = await OrchestratorRuntime().execute(
        run_id="run-1",
        conversation_id="conversation",
        work_dir=str(tmp_path),
        tasks=[review_task],
        executor=executor,
    )

    review = snapshot["tasks"][0]
    assert review["status"] == "completed"
    assert review["result"] == "Review complete: no blocking issues."
    assert review["audit"]["filesChanged"] == []


@pytest.mark.asyncio
async def test_runtime_records_workspace_audit_for_successful_write(tmp_path):
    async def executor(planned_task, workspace):
        (tmp_path / "created.txt").write_text("created", encoding="utf-8")
        return {"status": "success", "summary": "created file", "teamNotes": []}

    snapshot = await OrchestratorRuntime().execute(
        run_id="run-1",
        conversation_id="conversation",
        work_dir=str(tmp_path),
        tasks=[task("write", access_mode="write")],
        executor=executor,
    )

    write_task = snapshot["tasks"][0]
    assert write_task["status"] == "completed"
    assert write_task["audit"]["filesCreated"] == ["created.txt"]
    assert write_task["audit"]["filesChanged"] == ["created.txt"]


@pytest.mark.asyncio
async def test_runtime_preserves_task_execution_warnings(tmp_path):
    async def executor(planned_task, workspace):
        return {
            "status": "success",
            "summary": "degraded read",
            "teamNotes": [],
            "warnings": ["Adapter downgraded to llm"],
        }

    snapshot = await OrchestratorRuntime().execute(
        run_id="run-1",
        conversation_id="conversation",
        work_dir=str(tmp_path),
        tasks=[task("read")],
        executor=executor,
    )

    assert snapshot["warnings"] == ["Adapter downgraded to llm"]


@pytest.mark.asyncio
async def test_runtime_refreshes_shared_state_at_each_batch_barrier(tmp_path):
    refreshed_batches = []

    async def executor(planned_task, workspace):
        if planned_task["id"] == "second":
            assert refreshed_batches == ["batch-1"]
        return {"status": "success", "summary": planned_task["id"], "teamNotes": []}

    async def refresh(batch_results, batch):
        refreshed_batches.append(batch["id"])
        return {
            "teamBoardVersion": len(refreshed_batches),
            "projectStateVersion": len(refreshed_batches),
            "warnings": [],
        }

    snapshot = await OrchestratorRuntime().execute(
        run_id="run-1",
        conversation_id="conversation",
        work_dir=str(tmp_path),
        tasks=[task("first"), task("second", depends_on=["first"])],
        executor=executor,
        refresh_shared_state=refresh,
    )

    assert refreshed_batches == ["batch-1", "batch-2"]
    assert snapshot["teamBoardVersion"] == 2
    assert snapshot["projectStateVersion"] == 2
