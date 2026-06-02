# M3 DeepSeek Proxy Unblock Plan

## Goal

Prevent local DeepSeek planner calls from stalling the UI when the developer machine uses a SOCKS proxy.

## Scope

- Add SOCKS support for `httpx` so DeepSeek requests can honor local proxy settings.
- Ensure unexpected planner client exceptions are surfaced as `PlannerFailure`.
- Keep OpenCode and Codex adapter contracts unchanged.

## Contract Notes

- No shared type, REST, or WebSocket schema changes.
- No secrets are read, logged, or modified.

## Implementation Steps

- Update backend requirements to install `httpx` with SOCKS support.
- Add planner regression coverage for unexpected client exceptions.
- Wrap unexpected planner client failures into `PlannerFailure`.
- Restart backend after installing the dependency.

## Tests

- `cd backend && .venv/bin/python -m pytest tests/test_m3_planner.py::test_planner_wraps_unexpected_client_errors -q`
- `cd backend && .venv/bin/python -m pytest tests/test_m3_planner.py tests/test_m3_cli_adapters.py -q`

## Out of Scope

- Changing proxy values or `.env` secrets.
- Replacing DeepSeek with another planner backend.
