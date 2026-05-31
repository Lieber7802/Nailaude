# M3 Implementation Report

## Status

M3 implementation and the strict-review stabilization pass are complete for the
planned MVP scope.

## Implemented

- DeepSeek OpenAI-compatible client, `LLMProviderAdapter`, optional summarizers, and fake transports.
- OpenCode and Codex CLI adapters, process lifecycle management, health checks, and fallback resolution.
- Team Board, Team Notes, Project State, Orchestrator Run, and Task Run persistence with Alembic migration.
- Safe workspace scanning, Git inspection, batch snapshots, isolated read copies, and lightweight handoff envelopes.
- DeepSeek planner wrapper, four planner results, one bounded replan, validator, and deterministic scheduler.
- FIFO conversation queue, full snapshot persistence, cancellation, persisted reconnect restoration, warnings, and pause/resume interactions.
- Frontend orchestrator store, stale-sequence rejection, status batches, clarification cards, capability recommendations, elevated approval cards, Team Board, and Project State display.

## Strict-Review Stabilization

- Propagated cancellation into active adapters and CLI subprocesses; blocked
  Agent work now terminates promptly and cleanup remains idempotent.
- Added per-task filesystem audits, bounded snapshots, audit persistence,
  recent-change handoff hints, and write-task no-op failure enforcement.
- Added safe read-only execution fallback with visible warnings. Text-only
  downgrade cannot silently complete filesystem writes.
- Made `cannot_plan` a recoverable error, clarification submission atomic, and
  paused-job mutation scoped to conversation plus run ownership.
- Refreshed Team Board and Project State at every batch barrier; made Project
  State reads idempotent and hardened Team Board merge integrity.
- Reconciled memory-only non-terminal runs to explicit failure after restart and
  added bounded frontend reconnect backoff.
- Streamed DeepSeek SSE incrementally, aligned Alembic with app configuration,
  added global CLI concurrency limits, and kept broadcasts resilient to stale
  sockets.
- Lazy-loaded routes and preview features. The entry chunk is `233.06 kB` and
  the largest Workspace chunk is `485.78 kB`, with no large-chunk warning.

## Verification Evidence

- `cd backend && python -u -m pytest -q` -> `114 passed`
- `cd frontend && npm test` -> `3 passed`
- `cd frontend && npm run lint` -> passed
- `cd frontend && npm run build` -> passed without a chunk-size warning
- `git diff --check` -> passed
- Empty temporary SQLite database: `alembic upgrade head` -> passed
- Targeted Mock-first group-chat, blocked cancellation, and restart
  reconciliation smoke suite -> `4 passed`

## Optional External Smoke

- DeepSeek real health call skipped. The supplied secret was not persisted or echoed.
- OpenCode CLI help smoke passed.
- Codex desktop executable is not a usable CLI on this machine; fallback behavior is covered.
