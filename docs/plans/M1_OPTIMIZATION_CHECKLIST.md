# M1 Optimization Checklist

## Docs

- [x] `docs/plans/M1_OPTIMIZATION_PLAN.md` created.
- [x] `docs/plans/M1_OPTIMIZATION_CHECKLIST.md` created.
- [x] `docs/M1_OPTIMIZATION_SUMMARY.md` created after verification.
- [x] `DEVLOG.md` updated.

## Backend Tests

- [x] Message history returns persisted artifacts.
- [x] 422 validation errors use unified `ApiResponse`.
- [x] Unsafe `workDir` is rejected.
- [x] Malformed WebSocket JSON returns a structured error event.
- [x] WebSocket manager cleanup is regression-covered.

## Backend Implementation

- [x] `serialize_message()` supports artifacts and `agentName`.
- [x] `GET /conversations/{id}/messages` hydrates artifacts.
- [x] `RequestValidationError` is handled by unified response format.
- [x] Conversation type and workDir validation are in place.
- [x] Message content validation is in place.
- [x] WebSocket parsing and exception paths are guarded.
- [x] WebSocket disconnect is idempotent.
- [x] MockAdapter demo copy is readable.

## Frontend Implementation

- [x] WebSocket stale socket events are ignored.
- [x] WebSocket malformed server messages do not crash handlers.
- [x] `send()` reports failure instead of silently dropping messages.
- [x] Optimistic user messages reconcile by `clientMessageId`.
- [x] Historical message artifacts hydrate the artifact store.
- [x] Sending uses the active conversation participant before global default.
- [x] M1 workspace demo copy is readable.

## Verification

- [x] `cd backend && pytest -q` passes.
- [x] `cd frontend && npm run build` passes.
- [x] `cd frontend && npm audit --audit-level=moderate` reviewed.
- [x] Checklist reflects actual completed work.
