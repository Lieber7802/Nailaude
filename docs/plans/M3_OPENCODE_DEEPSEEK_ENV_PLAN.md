# M3 OpenCode DeepSeek Env Plan

## Goal

Allow OpenCode subprocesses to read the DeepSeek API key loaded by the backend from `backend/.env`.

## Scope

- Pass backend DeepSeek-related settings into `OpenCodeAdapter` child process environments.
- Keep secrets backend-only and never log or return them.
- Preserve Codex bridge behavior unchanged.

## Contract Notes

- No shared type, REST, or WebSocket schema changes.
- No `.env` secret values are written to repository files.
- OpenCode still uses `OPENCODE_MODEL`.

## Implementation Steps

- Add a regression test that asserts OpenCode process env includes DeepSeek keys.
- Add an OpenCode isolated env helper.
- Use the helper for normal and preview-repair OpenCode runs.
- Update checklist and DEVLOG.

## Tests

- `cd backend && .venv/bin/python -m pytest tests/test_m3_cli_adapters.py::test_opencode_adapter_passes_deepseek_env_to_child_process -q`
- `cd backend && .venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q`

## Out of Scope

- Reading or modifying real `.env` secret values.
- Changing OpenCode CLI installation or authentication files.
