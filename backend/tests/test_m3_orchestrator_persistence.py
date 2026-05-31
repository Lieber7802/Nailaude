import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models.conversation import Conversation
from app.models.orchestrator_run import OrchestratorRun
from app.models.task_run import TaskRun
from app.services.orchestrator_state import (
    latest_snapshot_for_conversation,
    persist_snapshot,
    reconcile_interrupted_snapshot,
    reconciled_snapshot_for_conversation,
)


@pytest.mark.asyncio
async def test_persist_snapshot_upserts_run_and_task_state():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        conversation = Conversation(title="Run", type="group", work_dir=".")
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        snapshot = {
            "runId": "run-1",
            "sequence": 3,
            "status": "executing",
            "reasoningSummary": "parallel",
            "warnings": [],
            "batches": [{"id": "batch-1", "index": 0, "status": "running", "taskIds": ["task-1"]}],
            "tasks": [
                {
                    "id": "task-1",
                    "agentId": "agent-1",
                    "accessMode": "read",
                    "status": "running",
                    "audit": {"filesChanged": ["src/app.py"]},
                }
            ],
        }

        await persist_snapshot(db, conversation.id, "message-1", snapshot)
        snapshot["sequence"] = 4
        snapshot["tasks"][0]["status"] = "completed"
        await persist_snapshot(db, conversation.id, "message-1", snapshot)

        run = await db.get(OrchestratorRun, "run-1")
        task = await db.scalar(select(TaskRun).where(TaskRun.run_id == "run-1"))
        latest = await latest_snapshot_for_conversation(db, conversation.id)
        assert run.sequence == 4
        assert task.status == "completed"
        assert task.audit == {"filesChanged": ["src/app.py"]}
        assert latest["sequence"] == 4
    await engine.dispose()


@pytest.mark.parametrize("status", ["queued", "planning", "awaiting_input", "awaiting_approval", "executing", "summarizing"])
def test_reconcile_interrupted_snapshot_marks_non_terminal_run_failed(status):
    snapshot = {
        "runId": "run-1",
        "sequence": 3,
        "status": status,
        "warnings": [],
        "updatedAt": "2026-05-31T10:00:00+00:00",
    }

    reconciled = reconcile_interrupted_snapshot(snapshot)

    assert reconciled["status"] == "failed"
    assert reconciled["sequence"] == 4
    assert "backend restart" in reconciled["warnings"][0]


def test_reconcile_interrupted_snapshot_preserves_terminal_run():
    snapshot = {"runId": "run-1", "sequence": 3, "status": "completed", "warnings": []}

    assert reconcile_interrupted_snapshot(snapshot) == snapshot


@pytest.mark.asyncio
async def test_reconciled_snapshot_persists_failed_restart_state():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        conversation = Conversation(title="Interrupted", type="group", work_dir=".")
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        snapshot = {
            "runId": "run-1",
            "sequence": 3,
            "status": "executing",
            "warnings": [],
            "tasks": [],
            "batches": [],
        }
        await persist_snapshot(db, conversation.id, "message-1", snapshot)

        reconciled = await reconciled_snapshot_for_conversation(db, conversation.id)
        run = await db.get(OrchestratorRun, "run-1")

        assert reconciled["status"] == "failed"
        assert run.status == "failed"
        assert run.latest_snapshot["status"] == "failed"
    await engine.dispose()
