"""Persistence helpers for latest full orchestrator snapshots."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orchestrator_run import OrchestratorRun
from app.models.task_run import TaskRun


async def persist_snapshot(db: AsyncSession, conversation_id: str, user_message_id: str, snapshot: dict) -> OrchestratorRun:
    run_id = str(snapshot["runId"])
    run = await db.get(OrchestratorRun, run_id)
    if run is None:
        run = OrchestratorRun(id=run_id, conversation_id=conversation_id, user_message_id=user_message_id)
        db.add(run)
    run.status = str(snapshot["status"])
    run.sequence = int(snapshot["sequence"])
    run.reasoning_summary = str(snapshot.get("reasoningSummary") or "")
    run.tasks = list(snapshot.get("tasks") or [])
    run.batches = list(snapshot.get("batches") or [])
    run.warnings = list(snapshot.get("warnings") or [])
    run.latest_snapshot = dict(snapshot)

    batch_by_task = {
        task_id: int(batch.get("index") or 0)
        for batch in snapshot.get("batches") or []
        for task_id in batch.get("taskIds") or []
    }
    for task in snapshot.get("tasks") or []:
        task_run = await db.scalar(
            select(TaskRun).where(TaskRun.run_id == run_id, TaskRun.task_id == str(task["id"]))
        )
        if task_run is None:
            task_run = TaskRun(
                run_id=run_id,
                task_id=str(task["id"]),
                agent_id=str(task["agentId"]),
                access_mode=str(task["accessMode"]),
            )
            db.add(task_run)
        task_run.batch_index = batch_by_task.get(str(task["id"]), 0)
        task_run.status = str(task.get("status") or "pending")
        task_run.result_summary = str(task.get("result") or "")
        task_run.audit = dict(task.get("audit") or {})
        task_run.error = str(task.get("error") or "") or None
    await db.commit()
    await db.refresh(run)
    return run


async def latest_snapshot_for_conversation(db: AsyncSession, conversation_id: str) -> dict | None:
    run = await db.scalar(
        select(OrchestratorRun)
        .where(OrchestratorRun.conversation_id == conversation_id)
        .order_by(OrchestratorRun.updated_at.desc())
    )
    return dict(run.latest_snapshot) if run and run.latest_snapshot else None


async def reconciled_snapshot_for_conversation(db: AsyncSession, conversation_id: str) -> dict | None:
    """Restore a reconnect snapshot and terminate memory-only interrupted work."""
    run = await db.scalar(
        select(OrchestratorRun)
        .where(OrchestratorRun.conversation_id == conversation_id)
        .order_by(OrchestratorRun.updated_at.desc())
    )
    if not run or not run.latest_snapshot:
        return None
    snapshot = dict(run.latest_snapshot)
    reconciled = reconcile_interrupted_snapshot(snapshot)
    if reconciled != snapshot:
        await persist_snapshot(db, run.conversation_id, run.user_message_id, reconciled)
    return reconciled


def reconcile_interrupted_snapshot(snapshot: dict) -> dict:
    """Make persisted in-memory-only work explicitly terminal after restart."""
    terminal = {"completed", "failed", "cancelled"}
    if snapshot.get("status") in terminal:
        return snapshot
    warning = "Run interrupted by backend restart; resend the request to continue"
    return {
        **snapshot,
        "sequence": int(snapshot.get("sequence") or 0) + 1,
        "status": "failed",
        "message": warning,
        "warnings": [*(snapshot.get("warnings") or []), warning],
        "updatedAt": datetime.now(timezone.utc).isoformat(),
    }
