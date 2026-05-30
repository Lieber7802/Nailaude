# M2 DeepSeek Adapter Plan

## Goal

Complete Xiaoma's M2 backend scope by making the `llm` platform usable through a DeepSeek OpenAI-compatible streaming adapter, while preserving the existing Mock-first chat core.

## Scope

- Implement `LLMProviderAdapter` for DeepSeek `/chat/completions` streaming.
- Keep API keys backend-only through environment variables; never write secrets to the repository.
- Add adapter factory and health checks in `AgentManagerService`.
- Let WebSocket dispatch choose an adapter by each Agent's `platform_id`, while builtin M2 Agents remain Mock-backed.
- Align Agent update routing with the API spec by supporting `PUT /agents/{id}` alongside existing `PATCH`.

## Contract Notes

- `PlatformId` remains `mock | llm | opencode | codex`.
- `LLMProviderAdapter.platform_name` must be `llm`.
- Adapter events remain `text_delta`, `file_created`, `file_modified`, `team_note`, `done`, and `error`.
- DeepSeek defaults come from official docs: `https://api.deepseek.com` and `deepseek-v4-flash`.
- `DEEPSEEK_API_KEY` is read only from runtime environment.

## Implementation Steps

1. Add failing tests for DeepSeek SSE parsing, missing API key behavior, AgentManager adapter selection, and PUT Agent updates.
2. Implement DeepSeek streaming with `httpx.AsyncClient.stream`.
3. Implement `AgentManagerService` factory and health checks.
4. Wire WebSocket task streaming through AgentManager without changing frontend contracts.
5. Update seed platform defaults and API documentation.
6. Run backend tests and frontend build.

## Tests

- `cd backend && pytest -q`
- `cd frontend && npm run build`

## Out of Scope

- OpenCode and Codex CLI process management.
- LLM Orchestrator decision-making.
- Writing API keys to `.env`.
- M4 preview/file watcher enhancements.
