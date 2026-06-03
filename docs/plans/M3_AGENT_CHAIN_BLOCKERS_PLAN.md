# M3 Agent Chain Blockers Plan

## Goal

Fix the three WSL/macOS-first blockers in the real AgentHub multi-agent chain: OpenCode output fidelity, DeepSeek health false negatives, and review-task false failures.

## Scope

Modify backend M3 components only:

- `backend/app/adapters/opencode.py`
- `backend/app/services/llm_client.py`
- `backend/app/services/orchestrator_runtime.py`
- Focused tests under `backend/tests/`
- `DEVLOG.md`

No shared type or frontend contract changes are expected.

## Contract Notes

- WebSocket event contracts stay unchanged: `text_delta`, `artifact`, `message_done`, `orchestrator_status`, `error`.
- Adapter output remains `AgentEvent` based.
- Runtime task statuses remain existing values: `completed`, `failed`, `blocked`, `cancelled`.
- WSL/macOS are the primary target environments for new CLI execution behavior.

## Implementation Steps

1. Add RED tests for `LLMClient.health_check()`:
   - It sends a larger JSON health request.
   - It returns true only when response JSON contains `ok: true`.

2. Add RED tests for runtime no-change review behavior:
   - A `write` task with review-like title/instruction and non-empty summary completes with no file changes.
   - Existing no-change write rejection still fails for build/create tasks.

3. Add RED tests for OpenCode server extraction/execution boundary:
   - Server-shaped nested response text is extracted as assistant text.
   - Adapter can run via a fake server executor and emit model text plus file events.
   - Existing CLI parser tests remain valid as fallback/parser coverage.

4. Implement `LLMClient.health_check()` fix:
   - Request `max_tokens=64` or another bounded value sufficient for `{"ok":true}`.
   - Return true only when parsed JSON has `ok is True`.

5. Implement runtime review exemption:
   - Add a small helper to classify review/validation tasks by title/objective/instruction.
   - Require non-empty summary to pass a no-change review task.
   - Preserve existing failure for non-review writes with no changes.

6. Implement OpenCode server primary path:
   - Start `opencode serve` on a loopback port selected by the OS.
   - Wait for `/global/health`.
   - Create a session with `POST /session`.
   - Send message with `POST /session/{id}/message`.
   - Recursively extract text/content from response objects, filtering reasoning/tool text where needed.
   - Kill the server process in `finally`.
   - Fall back to existing CLI `run --format json` helper if server startup or HTTP execution fails before any workspace result is available.

7. Run targeted tests in WSL:
   - `python -B -m pytest -q -p no:cacheprovider tests/test_m3_llm_client.py tests/test_m3_orchestrator_runtime.py tests/test_m3_cli_adapters.py`

8. Run a real WSL smoke:
   - DeepSeek direct/API health.
   - Codex adapter smoke.
   - OpenCode adapter smoke.
   - Group chain builder plus reviewer smoke.

9. Update checklist and `DEVLOG.md`.

10. Follow-up regression fix:
   - Add a RED test proving executor exception fallback results still carry `taskId`, `agentId`, and `batchId` into shared-state refresh.
   - Normalize runtime task metadata before audit/status post-processing so Team Board and Project State can refresh even when an adapter raises.

## Tests

Targeted:

```bash
cd backend
. .venv/bin/activate
PYTHONPATH=. python -B -m pytest -q -p no:cacheprovider \
  tests/test_m3_llm_client.py \
  tests/test_m3_orchestrator_runtime.py \
  tests/test_m3_cli_adapters.py
```

Broader when targeted tests pass:

```bash
cd backend
. .venv/bin/activate
PYTHONPATH=. python -B -m pytest -q -p no:cacheprovider tests/test_m3_websocket_runtime.py tests/test_m3_e2e.py
```

## Out of Scope

- Persistent OpenCode daemon pool.
- New UI task status components.
- New dependencies.
