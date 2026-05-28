# M3 DeepSeek LLM Backend Plan

## Goal

Switch the documented M3 LLM backend strategy to a private DeepSeek API for the competition MVP, while keeping OpenCode and Codex as the two Agent platforms required by the topic.

## Scope

- Document DeepSeek as the default LLM backend for Orchestrator decisions and LLMProvider fallback.
- Keep OpenCode and Codex as the two Agent platforms; DeepSeek is a model backend, not counted as a separate Agent platform.
- Record current DeepSeek v4 flash pricing assumptions for development/debug/testing budget planning.
- Clarify API key handling: backend-only environment variables, never committed, never exposed to frontend.
- Preserve MockAdapter as the deterministic fallback for development, CI, and demo safety.

## Contract Notes

- No shared type change in this documentation pass.
- No REST or WebSocket contract change in this documentation pass.
- `PlatformId` remains `mock | llm | opencode | codex`.
- Future implementation should route `llm` through a DeepSeek-compatible OpenAI-format client.

## Implementation Steps

1. Update `docs/PRD.md` platform/backend wording to DeepSeek-first.
2. Update `docs/TECH_DESIGN.md` architecture, fallback, environment examples, and M-series responsibilities.
3. Update `docs/TASK_BREAKDOWN.md` M2/M3 responsibility text and acceptance criteria.
4. Update `docs/API_SPEC.md` platform sample config for the `llm` provider.
5. Add a concise DeepSeek cost estimate and budget control strategy.
6. Update this checklist and append `DEVLOG.md`.

## Tests

- Documentation grep: no future-facing default LLM backend should point to the previous model provider.
- No runtime tests required because this task changes docs only.

## Out of Scope

- Implementing `LLMProviderAdapter`.
- Adding `DEEPSEEK_API_KEY` to `.env`.
- Changing OpenCode/Codex adapters.
- Changing shared types or API schemas.
