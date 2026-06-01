# M3 Builtin Agent OpenCode Plan

## Goal

Ensure the backend default implementation for `代码工匠`, `审查大师`, and `文档专家` uses `platformId=opencode`.

## Scope

- Update backend seed data for the three builtin Agent roles.
- Normalize existing builtin seed rows to `opencode` when backend seed runs.
- Keep REST and shared type contracts unchanged.
- Update API examples where they contradicted the new default.

## Contract Notes

- `PlatformId` already includes `opencode`.
- `GET /api/v1/agents` continues returning camelCase `platformId`.
- No WebSocket payload shape changes are required.

## Implementation Steps

1. Add a regression test that asserts the three builtin Agent names return `platformId=opencode`.
2. Update `backend/app/services/seed.py` defaults.
3. Update existing builtin rows during seed so older local databases converge to the requested backend state.
4. Refresh API documentation examples.

## Tests

- `cd backend && ../.venv/bin/python -m pytest tests/test_m1_1_api.py -q`
- `cd backend && ../.venv/bin/python -m pytest -q`

## Out of Scope

- Removing `mock`, `llm`, or `codex` platform support.
- Changing frontend display behavior.
