# M5 LLM-first Planner Plan

## Goal

Make Orchestrator Planner trust the LLM's semantic task-to-agent assignment when the returned `agentId` is a valid current participant. Backend keyword/stage logic should only repair malformed plans, not override valid planner decisions.

## Scope

- Update backend planner normalization and repair logic.
- Keep public REST, WebSocket, and shared TypeScript contracts unchanged.
- Keep planner retry, structural validation, explicit mention coverage, and MockAdapter behavior.
- Keep `accessMode` as compatibility metadata, but prevent keyword logic from overriding explicit valid values.

## Contract Notes

- `Task.agentId`, `Task.agentName`, `Task.accessMode`, and status snapshot payload shapes stay unchanged.
- Valid LLM `agentId` values are authoritative.
- Backend may repair missing or invalid agent ids by exact agent name first, then stage/profile fallback.
- `accessMode` no longer controls runtime permissions and no longer gets forced from explicit `read` to `write`.

## Implementation Steps

1. Add planner tests for ecommerce page requirements, review task wording, conflicting names, invalid id repair, accessMode preservation, and true explicit mention omissions.
2. Reorder `_resolve_agent_id()` so a valid participant `agentId` returns before stage/profile inference.
3. Keep name-based and stage-based repair for missing, alias-based, or invalid agent ids.
4. Normalize explicit `accessMode` casing without keyword-forcing valid `read` / `write` values.
5. Update API behavior notes, checklist, and DEVLOG.

## Tests

- `PYTHONPATH=backend backend/.venv/bin/python -m pytest backend/tests/test_m3_planner.py -q`
- `backend/.venv/bin/python -m pytest backend/tests/test_m3_planner.py backend/tests/test_m3_websocket_interactions.py backend/tests/test_m3_websocket_runtime.py -q`
- `backend/.venv/bin/python -m pytest backend/tests`
- `git diff --check`

## Out of Scope

- Removing planner entirely.
- Changing `packages/shared/types.ts`.
- Changing WebSocket message shapes.
- Changing frontend rendering.
