# M3 Agent Chain Blockers Spec

## Goal

Resolve the three WSL/macOS-first agent chain blockers found during the real WSL smoke:

1. OpenCode CLI `run --format json` starts successfully but often emits only protocol events, so chat text falls back to synthetic summaries.
2. DeepSeek-backed `LLMClient.health_check()` returns false even when the API is usable, causing avoidable adapter downgrades.
3. Review/validation tasks can return useful text but be marked failed because they ran in a write workspace and made no file changes.

## Runtime Assumptions

- Primary development/runtime targets are WSL and macOS.
- Windows-specific executable resolution remains supported where already implemented, but new fixes should not depend on Windows behavior.
- `MockAdapter` remains a permanent fallback and must not be removed.
- No shared type changes are required; the existing task, batch, warning, message, and artifact contracts are sufficient.

## Evidence Summary

### OpenCode Output Blocker

Observed in WSL with Linux-native OpenCode 1.15.13:

- `opencode run --format json --model deepseek/deepseek-v4-flash ...` returned rc 0.
- stdout contained only `{"type":"step_start", ...}` for a text-only prompt.
- Nailaude therefore emitted a fallback message such as "OpenCode completed..." instead of the model's final response.
- `opencode serve` health was true and `/session/:id/message` returned the nested model text, including `OPENCODE_SERVER_WSL_OK`.

Root cause: the CLI one-shot stdout stream is not a reliable source of final assistant text for the current OpenCode version. The server API is the more stable programmatic boundary.

Required behavior:

- `OpenCodeAdapter.run_task()` should prefer an OpenCode server/API execution path.
- It should still snapshot the workspace before/after and emit artifacts exactly as today.
- It should use fallback summaries only when the server response has no usable assistant text.
- It should keep the existing CLI stdout parser as a compatibility fallback or testable helper, not as the primary WSL/macOS path.

### LLM Health Blocker

Observed in WSL:

- Direct DeepSeek chat completion returned status 200 and `DEEPSEEK_WSL_OK`.
- `LLMClient.health_check()` returned false for `deepseek-v4-flash`.
- Prior experiments showed `max_tokens=16` can truncate the JSON health response.

Root cause: the health check is too strict and too token-constrained for models that include reasoning or do not return the exact small JSON within 16 tokens.

Required behavior:

- Health check must prove the configured API key/model can complete a minimal request.
- It should request enough tokens for the JSON result.
- It should validate semantic content (`ok is true`) instead of merely "request_json did not raise".
- It must still return false for missing API key or invalid JSON/API errors.

### Review Task False Failure

Observed in WSL real group chain:

- OpenCode builder wrote `index.html` and emitted a webpage artifact.
- Codex reviewer returned a useful review message.
- Runtime marked the review task failed because it had `accessMode=write` and no files changed.
- Final run still became `completed`, leaving a confusing UI state: review text appears, but task/batch status says failed.

Root cause: runtime enforces "successful write tasks must change files" for all write tasks, but review/validation tasks are often planned with write access only because they run after a writer and inspect the write workspace.

Required behavior:

- Keep rejecting build/create/modify write tasks that report success without file changes.
- Allow review/audit/inspect/validate/check tasks to complete without file changes when they return non-empty summary text.
- The audit should still record zero file changes.
- If a true write task produces no changes, the existing failure should remain.

## Out of Scope

- No frontend UI redesign.
- No changes to `packages/shared/types.ts`.
- No removal of CLI fallback behavior.
- No OpenCode long-lived shared daemon management beyond a per-task server lifecycle unless tests show a need.
