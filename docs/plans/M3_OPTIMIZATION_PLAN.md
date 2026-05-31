# M3 Optimization Plan

## Goal

Close every correctness, recovery, reliability, and maintainability gap listed in
`docs/plans/M3_OPTIMIZATION_CHECKLIST.md` while preserving the Mock-first M3
architecture.

## Scope

- Backend runtime cancellation, task audit, downgrade semantics, batch barriers,
  restart reconciliation, Project State idempotence, DeepSeek streaming, Team
  Board integrity, ProcessPool limits, migration configuration, bounded workspace
  snapshots, and resilient broadcasts.
- Frontend orchestrator protocol handling, atomic clarification submission,
  stale snapshot rejection, reconnect behavior, failed-send feedback, and route
  level code splitting.
- Regression coverage, migration smoke tests, manual Mock-first smoke, checklist
  completion, implementation report, and DEVLOG handoff.

## Contract Notes

- Preserve `MockAdapter` as a permanent fallback.
- Keep shared REST and WebSocket contracts aligned with
  `docs/M3_API_CONTRACT.md`, `docs/API_SPEC.md`, and
  `packages/shared/types.ts`.
- A `write` task succeeds only when its per-task workspace audit records a real
  file change.
- Downgrades and degraded execution remain visible in orchestrator snapshots.
- Persisted non-terminal runs are reconciled to an explicit terminal state after
  restart unless a complete resumable job can be restored.

## Implementation Steps

### Phase 1 - Runtime Safety And Audit

- [x] Add failing regressions for blocked cancellation, write-task no-op failure,
  workspace audit fields, adapter failure fallback, and ProcessPool concurrency.
- [x] Propagate cancellation into active adapters and terminate CLI subprocesses.
- [x] Capture per-task workspace diffs, persist audits, enforce write completion,
  and preserve downgrade warnings.

### Phase 2 - Protocol And Frontend State Machine

- [x] Add failing regressions for `cannot_plan`, atomic multi-question input,
  cross-conversation paused-job responses, stale snapshots, reconnect, and
  failed-send feedback.
- [x] Handle `cannot_plan` as a structured error, scope paused jobs by
  conversation and run, submit clarification answers atomically, reject stale
  snapshots before side effects, and reconnect with bounded backoff.

### Phase 3 - Shared State And Restart Recovery

- [x] Add failing regressions for batch-barrier refresh, restart reconciliation,
  Project State idempotence, Team Board membership/progress/ownership, and
  handoff metadata.
- [x] Refresh collaboration state after every batch, reconcile persisted
  non-terminal runs, split Project State reads from refreshes, and complete
  handoff context.

### Phase 4 - Reliability And Resource Bounds

- [x] Add failing regressions for incremental SSE streaming, migration
  configuration, bounded workspace snapshots, and partial broadcast failures.
- [x] Stream DeepSeek SSE incrementally, align Alembic with app settings, bound
  snapshot copying, remove stale sockets during broadcast, and lazy-load heavy
  frontend routes.

### Phase 5 - Verification And Handoff

- [x] Run targeted regressions after each phase.
- [x] Run backend, frontend lint/build, whitespace, migration, Mock-first,
  blocked cancellation, and restart reconciliation checks.
- [x] Update `docs/plans/M3_OPTIMIZATION_CHECKLIST.md`,
  `docs/plans/M3_IMPLEMENTATION_REPORT.md`, and `DEVLOG.md`.

## Tests

- `cd backend && pytest -q`
- `cd frontend && npm test`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`
- `git diff --check`
- `cd backend && alembic upgrade head` with a temporary SQLite URL
- Manual Mock-first group-chat WebSocket smoke

## Out Of Scope

- P2 product features.
- Replacing agent platforms.
- Removing `MockAdapter`.
- Unrelated frontend redesign.
