# M3 Codex CLI Integration Checklist

## Docs
- [x] Plan created.
- [x] Checklist created.
- [x] Contract reviewed.

## Implementation
- [x] Tests written first and verified failing.
- [x] Codex adapter uses current `codex exec --json --cd` CLI path.
- [x] Codex JSONL text output is converted to `text_delta`.
- [x] Codex file changes are converted to standard file AgentEvents.
- [x] Health check uses the real terminal `codex` command path.
- [x] DeepSeek Planner real-output variants are normalized before schema validation.

## Verification
- [x] Targeted CLI adapter tests pass.
- [x] Targeted Planner normalization tests pass.
- [x] Relevant runtime/manager tests pass.
- [x] Real local Codex CLI smoke completed or documented.
- [x] Real DeepSeek Planner + Codex CLI WebSocket smoke completed.
- [x] DEVLOG updated.
