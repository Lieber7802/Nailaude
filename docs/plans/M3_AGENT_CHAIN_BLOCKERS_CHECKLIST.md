# M3 Agent Chain Blockers Checklist

## Docs

- [x] Spec created for the three blockers.
- [x] Plan created for implementation and verification.
- [x] DEVLOG updated with final changes and evidence.

## Research

- [x] WSL OpenCode CLI `run --format json` observed returning only protocol events.
- [x] WSL OpenCode server API observed returning nested assistant text.
- [x] DeepSeek direct API observed healthy while `LLMClient.health_check()` returned false.
- [x] Real WSL group chain observed review text plus failed review task.

## Tests First

- [x] RED test for `LLMClient.health_check()` semantic `ok: true` and sufficient token budget.
- [x] RED test allowing no-change review/validation tasks with summary text.
- [x] RED test preserving failure for no-change build/write tasks.
- [x] RED test for OpenCode server response text extraction.
- [x] RED test for OpenCode adapter server execution path.
- [x] RED test for runtime executor exceptions preserving task metadata for shared-state refresh.

## Implementation

- [x] `LLMClient.health_check()` fixed.
- [x] Runtime no-change review/validation task classification implemented.
- [x] OpenCode server/API execution path implemented.
- [x] Runtime executor exception fallback preserves `taskId`, `agentId`, and `batchId`.
- [x] CLI parser kept as fallback/helper.
- [x] No shared type changes introduced.
- [x] MockAdapter preserved.

## Verification

- [x] Targeted WSL tests pass.
- [x] Broader M3 WebSocket/e2e tests pass or residual failures are explained.
- [x] Real WSL smoke shows OpenCode model text, artifact creation, Codex review text, and no false failed review task.
- [x] Windows workspace and WSL workspace statuses reviewed.
