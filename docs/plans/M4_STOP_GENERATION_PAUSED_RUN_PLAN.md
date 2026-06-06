# M4 Stop Generation Paused Run Plan

## Goal

Fix `stop_generation` so the terminate button cancels the current single chat run even when the run is paused for clarification or approval.

## Scope

- Backend WebSocket stop handling in `backend/app/ws/handlers.py`.
- Regression coverage in `backend/tests/test_m3_websocket_runtime.py`.
- Existing WebSocket payload shape stays unchanged.

## Contract Notes

- `packages/shared/types.ts` already defines `OrchestratorRunStatus` with `cancelled`.
- `docs/API_SPEC.md` defines `stop_generation` as cancelling the current active run and pre-execution windows.
- This fix extends the implementation to paused `awaiting_input` / `awaiting_approval` jobs without changing the client message schema.

## Implementation Steps

1. Add a regression test for cancelling a single conversation run while it is `awaiting_input`.
2. Route `stop_generation` through a helper that cancels active, queued, then paused jobs for the conversation.
3. Publish a `cancelled` snapshot for paused jobs and remove them from `paused_jobs`.
4. Verify focused WebSocket runtime tests.

## Tests

- `cd backend && .venv/bin/python -m pytest tests/test_m3_websocket_runtime.py::test_stop_generation_cancels_paused_input_run`
- `cd backend && .venv/bin/python -m pytest tests/test_m3_websocket_runtime.py::test_stop_generation_cancels_active_run tests/test_m3_websocket_runtime.py::test_stop_generation_cancels_paused_input_run`

## Out of Scope

- New UI controls.
- Shared type changes.
- Force-cancelling planner LLM calls already in progress.
