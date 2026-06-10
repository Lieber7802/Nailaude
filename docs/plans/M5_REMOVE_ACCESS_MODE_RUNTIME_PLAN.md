# M5 Remove Access Mode Runtime Plan

## Goal

Stop using planner-assigned read/write access as an operational permission model. All Nailaude tasks run inside the real conversation workspace, and accessMode no longer controls scheduling, workspace isolation, fallback, or success/failure.

## Scope

- Backend scheduler batching.
- Backend runtime workspace selection and no-change validation.
- Adapter prompt contracts that currently depend on `accessMode`.
- Focused regression tests and API documentation note.

## Contract Notes

- `packages/shared/types.ts` remains unchanged for compatibility. `Task.accessMode` is retained as planner metadata, not an execution permission.
- Runtime should no longer create read-only temporary copies for read tasks.
- Runtime should no longer fail a task solely because no workspace files changed.
- Preview/review prompt behavior should be inferred from task intent, not accessMode.

## Implementation Steps

1. Add failing tests for same-batch execution, real-workspace handoff, and no-change completion.
2. Remove the scheduler write-slot limit.
3. Run every task against `write_workspace` and set handoff workspace access metadata to `write`.
4. Remove write/no-change failure enforcement.
5. Relax preview/review contract helpers so accessMode is no longer the deciding gate.
6. Update docs and DEVLOG.

## Tests

- `backend/tests/test_m3_scheduler.py`
- `backend/tests/test_m3_orchestrator_runtime.py`
- `backend/tests/test_m3_websocket_runtime.py`
- `backend/tests/test_m3_cli_adapters.py`

## Out of Scope

- Removing `accessMode` from shared types, database records, or Planner schema.
- Reworking security boundaries outside the project workspace.
- Changing CLI sandbox flags.
