"""Batch-oriented M3 Orchestrator runtime."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from inspect import isawaitable

from app.schemas.orchestrator import PlannedTask
from app.services.orchestrator_scheduler import OrchestratorScheduler
from app.services.workspace_snapshot import WorkspaceSnapshotService


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


class OrchestratorRuntime:
    def __init__(self, scheduler: OrchestratorScheduler | None = None, snapshot_service: WorkspaceSnapshotService | None = None):
        self.scheduler = scheduler or OrchestratorScheduler()
        self.snapshot_service = snapshot_service or WorkspaceSnapshotService()
        self._cancel_events: dict[str, asyncio.Event] = {}
        self._cancelled_before_start: set[str] = set()

    def cancel(self, run_id: str) -> None:
        event = self._cancel_events.get(run_id)
        if event:
            event.set()
            return
        self._cancelled_before_start.add(run_id)

    async def execute(
        self,
        *,
        run_id: str,
        conversation_id: str,
        work_dir: str,
        tasks: list[dict],
        executor,
        emit=None,
        refresh_shared_state=None,
        reasoning_summary: str = "",
        initial_sequence: int = 0,
    ) -> dict:
        created_at = utc_timestamp()
        cancel_event = asyncio.Event()
        if run_id in self._cancelled_before_start:
            cancel_event.set()
        self._cancel_events[run_id] = cancel_event
        task_models = [PlannedTask.model_validate(task) for task in tasks]
        task_state = {task.id: {**task.model_dump(by_alias=True), "status": "pending"} for task in task_models}
        batches = self.scheduler.schedule(task_models)
        sequence = initial_sequence
        warnings: list[str] = []
        team_board_version = 0
        project_state_version = 0

        async def send(status: str, message: str, current_batch_index: int | None = None) -> dict:
            nonlocal sequence
            sequence += 1
            snapshot = {
                "runId": run_id,
                "sequence": sequence,
                "status": status,
                "message": message,
                "reasoningSummary": reasoning_summary,
                "currentBatchIndex": current_batch_index,
                "totalBatches": len(batches),
                "tasks": list(task_state.values()),
                "batches": batches,
                "warnings": list(warnings),
                "teamBoardVersion": team_board_version,
                "projectStateVersion": project_state_version,
                "createdAt": created_at,
                "updatedAt": utc_timestamp(),
            }
            if emit:
                emitted = emit(snapshot)
                if isawaitable(emitted):
                    await emitted
            return snapshot

        latest = await send("executing", "Starting orchestrator run")
        try:
            for batch in batches:
                batch_index = batch["index"]
                if cancel_event.is_set():
                    break
                runnable = []
                for task_id in batch["taskIds"]:
                    task = task_state[task_id]
                    dependency_states = [task_state[item]["status"] for item in task["dependsOn"]]
                    if any(state in {"failed", "blocked", "cancelled"} for state in dependency_states):
                        task["status"] = "blocked"
                    else:
                        task["status"] = "running"
                        task["startedAt"] = task.get("startedAt") or utc_timestamp()
                        task["endedAt"] = None
                        runnable.append(task)
                batch["status"] = "running"
                latest = await send("executing", f"Executing batch {batch_index + 1} / {len(batches)}", batch_index)
                if not runnable:
                    batch["status"] = "failed"
                    continue
                snapshot = self.snapshot_service.create_batch_snapshot(work_dir)
                warnings.extend(snapshot.warnings)
                try:
                    async def run_task(task: dict) -> tuple[dict, dict]:
                        workspace = self.snapshot_service.write_workspace(work_dir, snapshot)
                        workspace.batch_id = batch["id"]
                        workspace.cancel_event = cancel_event
                        before = self.snapshot_service.capture_workspace_state(workspace.path)
                        try:
                            result = await executor(task, workspace)
                        except Exception as exc:
                            result = {"status": "failed", "summary": "", "error": str(exc), "teamNotes": []}
                        result = self._with_task_metadata(task, workspace.batch_id, result)
                        after = self.snapshot_service.capture_workspace_state(workspace.path)
                        audit = self.snapshot_service.diff_workspace_states(before, after)
                        result.update({**audit, "audit": audit})
                        return task, result

                    workers = [asyncio.create_task(run_task(task)) for task in runnable]
                    gather = asyncio.gather(*workers)
                    cancel_wait = asyncio.create_task(cancel_event.wait())
                    done, _ = await asyncio.wait({gather, cancel_wait}, return_when=asyncio.FIRST_COMPLETED)
                    if cancel_wait in done and gather not in done:
                        for worker in workers:
                            worker.cancel()
                        await asyncio.gather(*workers, return_exceptions=True)
                        results = []
                    else:
                        results = await gather
                    cancel_wait.cancel()
                finally:
                    self.snapshot_service.cleanup(snapshot)
                failures = 0
                for task, result in results:
                    task["audit"] = result.get("audit") or {}
                    warnings.extend(str(item) for item in result.get("warnings") or [])
                    if cancel_event.is_set():
                        task["status"] = "cancelled"
                        task["endedAt"] = task.get("endedAt") or utc_timestamp()
                    elif result.get("status") == "success":
                        task["status"] = "completed"
                        task["result"] = result.get("summary", "")
                        task["endedAt"] = task.get("endedAt") or utc_timestamp()
                    else:
                        failures += 1
                        task["status"] = "failed"
                        task["result"] = result.get("error") or result.get("summary", "")
                        task["endedAt"] = task.get("endedAt") or utc_timestamp()
                if cancel_event.is_set():
                    for task in runnable:
                        task["status"] = "cancelled"
                        task["endedAt"] = task.get("endedAt") or utc_timestamp()
                    batch["status"] = "cancelled"
                    break
                batch["status"] = "failed" if failures == len(runnable) else "partial" if failures else "completed"
                if refresh_shared_state:
                    try:
                        versions = await refresh_shared_state([result for _, result in results], batch)
                        if versions:
                            team_board_version = int(versions.get("teamBoardVersion") or 0)
                            project_state_version = int(versions.get("projectStateVersion") or 0)
                            warnings.extend(str(item) for item in versions.get("warnings") or [])
                    except Exception as exc:
                        warnings.append(f"Shared state refresh warning: {exc}")
                latest = await send("executing", f"Completed batch {batch_index + 1} / {len(batches)}", batch_index)

            if cancel_event.is_set():
                for task in task_state.values():
                    if task["status"] in {"pending", "ready"}:
                        task["status"] = "cancelled"
                for batch in batches:
                    if batch["status"] == "pending":
                        batch["status"] = "cancelled"
                latest = await send("cancelled", "Run cancelled")
                return latest

            latest = await send("summarizing", "Finalizing shared state")
            latest = await send("completed", "Run completed")
            return latest
        finally:
            self._cancel_events.pop(run_id, None)
            self._cancelled_before_start.discard(run_id)

    def _with_task_metadata(self, task: dict, batch_id: str, result: dict) -> dict:
        result.setdefault("taskId", task["id"])
        result.setdefault("agentId", task["agentId"])
        result.setdefault("batchId", batch_id)
        return result
