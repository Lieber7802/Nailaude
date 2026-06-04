# M3 Agent Chain Blockers Plan

## Goal

Fix the three WSL/macOS-first blockers in the real AgentHub multi-agent chain: OpenCode output fidelity, DeepSeek health false negatives, and review-task false failures.

## Scope

Modify backend M3 components only:

- `backend/app/adapters/opencode.py`
- `backend/app/adapters/codex.py`
- `backend/app/services/deepseek_responses_bridge.py`
- `backend/app/services/llm_client.py`
- `backend/app/services/orchestrator_planner.py`
- `backend/app/services/orchestrator_runtime.py`
- `backend/app/services/planner_prompt.py`
- `backend/app/services/process_pool.py`
- `backend/app/ws/handlers.py`
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

11. Follow-up Codex/DeepSeek bridge fixes:
   - Add RED tests for large Codex tool outputs, DeepSeek error-body propagation, reasoning-content round-trip, and consecutive function-call grouping.
   - Truncate large `function_call_output` payloads before forwarding to DeepSeek.
   - Preserve DeepSeek `reasoning_content` across tool-call turns.
   - Group consecutive Responses `function_call` items into one Chat Completions assistant `tool_calls` message before tool outputs.

12. Follow-up planner coverage fixes:
   - Add a RED test proving omitted explicit mentions or requested stages trigger one validation-guided replan.
   - Strengthen the planner prompt for multi-Agent requirements / implementation / review / README workflows.
   - Add deterministic contextual coverage validation for explicitly mentioned agents and requested stages.

13. Follow-up runtime environment fixes:
   - Keep isolated Codex homes outside `/tmp` for WSL compatibility.
   - Send Codex prompts through stdin instead of argv.
   - Preserve stdout in `ProcessPoolError` when stderr is empty.
   - Materialize SQLAlchemy scalar results once in WebSocket planning so available-agent validation is not accidentally disabled.

14. Follow-up planner strictness and stabilization fixes:
   - Add RED tests for Markdown-wrapped/invalid DeepSeek JSON content diagnostics.
   - Add RED tests for DeepSeek loose planner field aliases such as `taskId`, `assignedAgentId`, `readAccess`, `writeAccess`, and top-level dependency tables.
   - Add RED tests for invalid copied agent ids being repaired from task stage/capability context when possible.
   - Strengthen the planner prompt with exact schema shapes, field-name restrictions, exact agent id copy rules, and staged workflow ordering.
   - Normalize common loose fields into the shared planner schema before Pydantic validation.
   - Enforce common app workflow dependencies: requirements -> implementation -> review -> README.
   - Verify the real Pomodoro planner request repeatedly without executing agents.

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
