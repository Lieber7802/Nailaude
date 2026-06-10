# M1 Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use the Nailaude module development workflow and test-driven-development. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the M1 happy-path implementation into a sturdier baseline by fixing persistence recovery, WebSocket error handling, REST error consistency, frontend connection races, basic path safety, and demo copy.

**Architecture:** Keep the current Mock-first M1 shape. Backend fixes stay in REST serializers/routes, WebSocket handlers, and schema validation. Frontend fixes stay in API/WS services, stores, and workspace hydration without changing `packages/shared/types.ts`.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 async, pytest, React 19, Vite, TypeScript, Zustand.

---

## Scope

- Fix M1 review findings that affect baseline stability and demo quality.
- Preserve existing API/WS contracts from `docs/API_SPEC.md` and `packages/shared/types.ts`.
- Do not add new runtime dependencies.
- Do not implement non-M1 features such as real OpenCode/Codex execution, Orchestrator scheduling, or preview file serving.

## Target Files

- `backend/tests/test_m1_1_api.py`: REST regression coverage for validation errors, workDir safety, and artifact recovery.
- `backend/tests/test_m1_2_websocket.py`: WebSocket malformed payload coverage and persistence recovery checks.
- `backend/app/api/serializers.py`: hydrate message artifacts and agent names.
- `backend/app/api/messages.py`: load artifacts with message history.
- `backend/app/api/responses.py`: validation error response helper.
- `backend/app/main.py`: register FastAPI request validation handler.
- `backend/app/schemas/conversation.py`: validate conversation type and workDir boundary.
- `backend/app/schemas/message.py`: validate non-empty message content.
- `backend/app/ws/handlers.py`: guarded JSON parsing, finally disconnect, safer partial-failure persistence.
- `backend/app/ws/manager.py`: idempotent disconnect.
- `backend/app/adapters/mock.py`: restore readable demo text.
- `frontend/src/services/websocket.ts`: stale socket guard, parse failure guard, send result.
- `frontend/src/hooks/useWebSocket.ts`: support server user-message acknowledgement and artifact hydration flow.
- `frontend/src/stores/messageStore.ts`: replace optimistic messages and attach artifacts from history.
- `frontend/src/stores/artifactStore.ts`: hydrate/reset artifact lists from history.
- `frontend/src/pages/Workspace.tsx`: default participant selection, error handling, clientMessageId, readable copy.
- `frontend/src/components/chat/MessageBubble.tsx`: read message artifacts plus artifact store.
- `frontend/src/components/preview/PreviewPanel.tsx`: readable empty state.
- `DEVLOG.md`: record this optimization pass.
- `docs/M1_OPTIMIZATION_SUMMARY.md`: final work sedimentation.

## Tasks

### Task 1: Backend Regression Tests

- [ ] Add tests proving message history returns persisted artifacts.
- [ ] Add tests proving 422 validation errors use `ApiResponse`.
- [ ] Add tests proving unsafe `workDir` is rejected.
- [ ] Add tests proving malformed WebSocket JSON returns an `error` event instead of crashing.
- [ ] Run targeted backend tests and confirm the new tests fail before implementation.

### Task 2: Backend Fixes

- [ ] Update message serialization to include artifacts and optional `agentName`.
- [ ] Load artifacts when listing messages.
- [ ] Add `RequestValidationError` handling through the unified response helper.
- [ ] Validate `ConversationCreate.type` and `workDir`.
- [ ] Validate non-empty message content.
- [ ] Harden WebSocket parsing and cleanup with recoverable error events and idempotent disconnect.
- [ ] Keep MockAdapter permanent and restore readable demo text.

### Task 3: Frontend Regression-Safe Fixes

- [ ] Guard stale WebSocket events so old sockets cannot overwrite the new status.
- [ ] Guard WebSocket JSON parse failures.
- [ ] Return a boolean from `send()` so the UI can avoid optimistic writes when closed.
- [ ] Add `clientMessageId` to WS sends and reconcile the server-persisted user message.
- [ ] Hydrate artifact store from historical message responses.
- [ ] Use active conversation participants when mentioning agents.
- [ ] Restore readable M1 demo copy.

### Task 4: Verification and Documentation

- [ ] Run `cd backend && pytest -q`.
- [ ] Run `cd frontend && npm run build`.
- [ ] Run `cd frontend && npm audit --audit-level=moderate`.
- [ ] Update this checklist with actual status.
- [ ] Update `DEVLOG.md`.
- [ ] Create `docs/M1_OPTIMIZATION_SUMMARY.md` with fixes, tests, and remaining risks.

## Acceptance Criteria

- Historical message loading can restore agent artifacts and the right preview payload.
- REST validation errors return `{ success, data, error, timestamp }`.
- Unsafe `workDir` values outside `workspaces/` are rejected.
- Malformed WS payloads return a structured `error` event and do not leave stale manager state.
- Frontend WebSocket status is not overwritten by stale socket events.
- Optimistic user messages reconcile to server ids when the backend acknowledges them.
- UI/Mock demo text is readable Chinese.
- Backend tests and frontend build pass.

## Out of Scope

- Real Agent CLI execution.
- Full multi-agent orchestration.
- Static preview file server.
- Changing shared TypeScript contracts.
