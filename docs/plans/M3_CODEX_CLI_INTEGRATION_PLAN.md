# M3 Codex CLI Integration Plan

## Goal

Complete the M3 Codex CLI adapter path now that `codex` is available on this machine. The adapter should use the current non-interactive Codex CLI, stream useful text through Nailaude events, and surface file changes as standard artifact-producing events.

## Scope

- Update `backend/app/adapters/codex.py`.
- Update `backend/app/services/orchestrator_planner.py`.
- Extend `backend/tests/test_m3_cli_adapters.py`.
- Extend `backend/tests/test_m3_planner.py`.
- Update `docs/CLI_AGENT_RESEARCH.md`.
- Record verification in `DEVLOG.md`.

## Contract Notes

- Keep the existing `AgentAdapter.run_task(work_dir, instruction, context)` contract.
- Yield only existing `AgentEvent` types: `text_delta`, `file_created`, `file_modified`, `error`, and `done`.
- Do not change `packages/shared/types.ts` or WebSocket contracts.
- Preserve the permanent `MockAdapter` fallback and AgentManager fallback behavior.

## Implementation Steps

1. Build a Codex prompt from task instruction plus sanitized handoff context.
2. Invoke `codex exec --json --cd <work_dir> --sandbox workspace-write --ask-for-approval never --skip-git-repo-check <prompt>`.
3. Parse JSONL stdout for final assistant text or message delta events.
4. Snapshot workspace files before and after execution and emit file events for created/modified text files.
5. Keep health check aligned with the real `codex --help` command.
6. Normalize common DeepSeek Planner output variants into the M3 planner contract.

## Tests

- Verify Codex command arguments use the current CLI.
- Verify JSONL final text becomes `text_delta`.
- Verify created and modified files become `file_created` and `file_modified`.
- Verify process errors still yield `error` then `done`.
- Verify real-model Planner variants such as `Ready`, `plan.tasks`, `readWriteAccess`, `description`, and string `acceptanceCriteria`.

## Out of Scope

- OpenCode session support.
- New frontend UI.
- New shared types or API endpoints.
