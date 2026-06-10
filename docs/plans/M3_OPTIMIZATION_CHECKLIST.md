# M3 Optimization Checklist

> **For agentic workers:** REQUIRED SUB-SKILL: Use the Nailaude module development workflow, systematic-debugging, and test-driven-development. Fix items in priority order. Add a failing regression test before each behavior change. Do not mark an item complete until its verification command passes.

## Goal

Close the correctness and recovery gaps found during the strict M3 review before acceptance. Preserve the existing Mock-first architecture, keep `MockAdapter` as a permanent fallback, and avoid unrelated refactors.

## Review Baseline

- Review date: `2026-05-31`
- Backend baseline: `cd backend && pytest -q` -> `76 passed`
- Frontend baseline: `cd frontend && npm run lint` -> passed
- Frontend baseline: `cd frontend && npm run build` -> passed with a `747.20 kB` main chunk warning
- Diff baseline: `git diff --check` -> no whitespace errors
- Migration smoke: Alembic upgrade succeeds on a fresh SQLite database when the URL is explicitly overridden

Passing baseline tests do not prove the M3 runtime semantics below. The P0 and P1 items need new regression coverage.

---

## P0 - Must Fix Before Acceptance

### [ ] P0-1 Stop generation must terminate active Agent work

**Problem**

`stop_generation` only sets a cancellation event. The runtime still waits for the currently executing Agent task to return, and the CLI adapters do not pass the cancellation signal into `ProcessPool`.

**Evidence**

- `backend/app/ws/handlers.py:79-84`
- `backend/app/services/orchestrator_runtime.py:23-26`
- `backend/app/services/orchestrator_runtime.py:111`
- `backend/app/services/process_pool.py:34`
- `backend/app/adapters/codex.py:33`
- `backend/app/adapters/opencode.py:33-36`
- `docs/plans/M3_ORCHESTRATOR_COORDINATION_DESIGN.md:612`

**Required Fix**

- [x] Propagate the run cancellation signal into active adapter executions.
- [x] Terminate the active CLI subprocess when a run is cancelled.
- [x] Ensure runtime cancellation does not wait indefinitely for an unresponsive Agent.
- [x] Keep cleanup idempotent when cancellation races with normal process exit.
- [x] Add a regression test with a blocked executor proving cancellation completes without manually releasing the executor.

**Acceptance**

- [x] A blocked Agent task exits promptly after `stop_generation`.
- [x] The run snapshot reaches `cancelled`.
- [x] No child process remains registered in `ProcessPool`.

### [ ] P0-2 Write tasks must not report false success after adapter downgrade

**Problem**

When a CLI adapter is unavailable, `AgentManagerService` can downgrade a `write` task to `LLMProviderAdapter`. The LLM adapter only emits text and `done`; it does not modify files. The runtime can still mark the task as completed.

**Evidence**

- `backend/app/services/agent_manager.py:38-48`
- `backend/app/adapters/llm_provider.py:27-37`
- `backend/app/ws/handlers.py:343-363`
- `backend/app/services/orchestrator_runtime.py:118-120`

**Required Fix**

- [x] Define explicit completion rules for `write` tasks.
- [x] Compare workspace state before and after a write task.
- [x] Return `failed` or `needs_review` when a write task produces no expected file change.
- [x] Preserve downgrade warnings in the final run snapshot and user-visible status.
- [x] Add regression tests for CLI unavailable, LLM downgrade, and no-files-changed cases.

**Acceptance**

- [x] A text-only LLM response cannot silently complete a filesystem write task.
- [x] Users can see when execution was downgraded.

---

## P1 - Fix In The M3 Stabilization Pass

### [ ] P1-1 Handle `cannot_plan` as a first-class Planner result

**Problem**

The Planner schema allows `cannot_plan`, but the WebSocket handler treats every non-ready plan as `awaiting_input`. The frontend input card assumes clarification questions or a capability gap and can receive an incompatible payload.

**Evidence**

- `backend/app/schemas/orchestrator.py:87-90`
- `backend/app/ws/handlers.py:267-273`
- `packages/shared/types.ts:434`
- `frontend/src/components/cards/OrchestratorInputCard.tsx:10`
- `frontend/src/components/cards/OrchestratorInputCard.tsx:32`

**Required Fix**

- [x] Add an explicit protocol branch for `cannot_plan`, or convert it to a structured recoverable error.
- [x] Render a safe user-facing message without assuming `questions`.
- [x] Add backend contract and frontend rendering tests.

### [ ] P1-2 Submit multi-question clarification atomically

**Problem**

The backend allows up to ten clarification questions, but the UI submits one answer at a time. The backend removes the paused job after the first response, so the remaining questions cannot be answered.

**Evidence**

- `backend/app/schemas/orchestrator.py:76-78`
- `frontend/src/components/cards/OrchestratorInputCard.tsx:32-67`
- `backend/app/ws/handlers.py:184-214`

**Required Fix**

- [x] Collect all answers in one frontend form and submit them together, or implement an explicit incremental answer accumulator.
- [x] Keep the paused job until all required answers are accepted.
- [x] Add an end-to-end test with at least two questions.

### [ ] P1-3 Refresh Team Board and Project State at every batch barrier

**Problem**

Shared state is merged only after the entire run finishes. Downstream batches cannot consume notes, decisions, or project summaries produced by earlier batches.

**Evidence**

- `backend/app/services/orchestrator_runtime.py:138-148`
- `backend/app/ws/handlers.py:365-388`
- `docs/plans/M3_ORCHESTRATOR_COORDINATION_DESIGN.md:304-317`

**Required Fix**

- [x] Add a batch-complete callback or equivalent runtime barrier.
- [x] Merge Team Notes and refresh Project State after each batch.
- [x] Pass the updated summary and standards into downstream task handoffs.
- [x] Broadcast refreshed collaboration snapshots after each barrier.
- [x] Add a two-batch regression test proving batch 2 receives batch 1 state.

### [ ] P1-4 Reconcile persisted runs after restart and reconnect automatically

**Problem**

Persisted snapshots restore the display only. Runtime queues and paused jobs are module-level memory structures. After a backend restart, the UI can show a run as active while no execution or resume path exists. The frontend WebSocket client also has no automatic reconnect policy.

**Evidence**

- `backend/app/ws/handlers.py:37-41`
- `backend/app/ws/handlers.py:59-64`
- `backend/app/ws/handlers.py:186`
- `backend/app/ws/handlers.py:222`
- `frontend/src/services/websocket.ts:19-35`
- `docs/M3_API_CONTRACT.md:71-72`

**Required Fix**

- [x] Define restart reconciliation for `executing`, `awaiting_input`, and `awaiting_approval`.
- [x] Restore resumable paused jobs from persisted data, or mark unrecoverable runs with an explicit terminal status.
- [x] Add bounded frontend reconnect with backoff and cancellation on conversation change.
- [x] Add restart and reconnect tests.

### [ ] P1-5 Reject stale snapshots before any frontend side effect

**Problem**

`orchestratorStore` rejects stale sequence numbers, but `useWebSocket` still updates UI status and clears cards unconditionally. An out-of-order snapshot can regress the visible state or dismiss an active input card.

**Evidence**

- `frontend/src/stores/orchestratorStore.ts:29-34`
- `frontend/src/hooks/useWebSocket.ts:58-62`

**Required Fix**

- [x] Make snapshot acceptance return whether the snapshot was applied.
- [x] Update banners, cards, and derived state only after accepted snapshots.
- [x] Add an out-of-order WebSocket regression test.

### [ ] P1-6 Validate conversation ownership before mutating paused jobs

**Problem**

Approval responses do not validate conversation ownership. Input responses remove the paused job before validation. A response from another conversation can cancel or consume an unrelated paused job.

**Evidence**

- `backend/app/ws/handlers.py:184-193`
- `backend/app/ws/handlers.py:220-234`

**Required Fix**

- [x] Resolve the paused job without removing it first.
- [x] Validate both `runId` and `conversationId` before mutation.
- [x] Scope paused-job storage by conversation and run.
- [x] Add cross-conversation rejection tests for input and approval responses.

### [ ] P1-7 Make Project State reads side-effect free

**Problem**

`GET /project-state` calls `refresh()`. Existing state increments its version even when the workspace fingerprint is unchanged. Repeated reads create version drift.

**Evidence**

- `backend/app/api/orchestrator.py:14-20`
- `backend/app/services/project_state.py:41-56`
- `frontend/src/pages/Workspace.tsx:97-104`
- `frontend/src/hooks/useWebSocket.ts:73-75`

**Required Fix**

- [x] Split read and refresh operations.
- [x] Increment the Project State version only after a meaningful state change.
- [x] Add tests proving repeated GET requests are idempotent.

### [ ] P1-8 Stream DeepSeek responses incrementally

**Problem**

The current DeepSeek client waits for a complete HTTP response and then splits `response.text`. Users receive no real token stream during long requests.

**Evidence**

- `backend/app/services/llm_client.py:67-86`
- `backend/app/services/llm_client.py:108-117`
- `backend/tests/test_m3_llm_client.py:35-53`

**Required Fix**

- [x] Use an HTTP streaming context and iterate lines incrementally.
- [x] Preserve timeout, retry, and malformed-frame behavior.
- [x] Add a test transport that yields multiple delayed SSE chunks.

### [ ] P1-9 Implement per-task workspace diff audit

**Problem**

The shared contract describes file audit fields, but task execution does not populate them. `recentChanges` and handoff navigation hints remain empty, so completion cannot be verified reliably.

**Evidence**

- `packages/shared/types.ts:284-292`
- `backend/app/ws/handlers.py:341`
- `backend/app/ws/handlers.py:354-361`
- `backend/app/services/project_state.py:78`
- `docs/plans/M3_ORCHESTRATOR_COORDINATION_DESIGN.md:499-502`

**Required Fix**

- [x] Capture workspace state before and after each task.
- [x] Persist changed files, audit summary, and relevant warnings.
- [x] Feed recent changes and navigation hints into later handoffs.
- [x] Use the audit result to enforce P0-2 write-task completion rules.

---

## P2 - Reliability And Maintainability Improvements

### [ ] P2-1 Align Alembic and application database configuration

- Evidence: `backend/alembic.ini:89`, `backend/alembic/env.py:30`, `backend/app/config.py:10`, `backend/app/database.py:9`, `backend/app/main.py:20`
- [x] Derive Alembic URL from the application settings or an explicit deployment override.
- [x] Avoid relying on `create_all()` for non-test schema upgrades.
- [x] Add a fresh-database migration test and an upgrade-from-previous-schema test.

### [ ] P2-2 Add a global ProcessPool concurrency limit

- Evidence: `backend/app/services/process_pool.py:19-27`
- [x] Add a configurable global semaphore for CLI subprocesses across conversations.
- [x] Add concurrency and cleanup tests.

### [ ] P2-3 Handle execution-time adapter failures and propagate warnings

- Evidence: `backend/app/adapters/opencode.py:32-43`, `backend/app/adapters/codex.py:32-37`, `backend/app/services/orchestrator_runtime.py:115-125`
- [x] Distinguish health-check success from execution success.
- [x] Retry through a safe fallback only when task semantics allow it.
- [x] Surface fallback and degraded-execution warnings in snapshots.

### [ ] P2-4 Harden Team Board state integrity

- Evidence: `backend/app/services/team_protocol.py:26-34`, `backend/app/services/team_protocol.py:64-68`, `backend/app/services/team_protocol.py:151-176`
- [x] Populate team members from the active conversation.
- [x] Merge completed task ids without erasing prior progress.
- [x] Validate conversation ownership before resolving Team Notes.
- [x] Review decision-conflict detection so unrelated decisions do not become false conflicts.

### [ ] P2-5 Report disconnected input and approval sends

- Evidence: `frontend/src/components/cards/OrchestratorInputCard.tsx:18-20`, `frontend/src/components/cards/OrchestratorApprovalCard.tsx:9-13`
- [x] Disable or report submission when WebSocket send fails.
- [x] Preserve the user input for retry after reconnect.

### [ ] P2-6 Complete handoff context metadata

- Evidence: `backend/app/ws/handlers.py:331-352`, `backend/app/ws/handlers.py:405-420`, `backend/app/services/handoff_builder.py:29-42`
- [x] Pass the real scheduler batch id instead of a snapshot id.
- [x] Include recent conversation summary in Planner context.
- [x] Add contract tests for generated handoffs.

### [ ] P2-7 Bound workspace snapshot resource usage

- Evidence: `backend/app/services/workspace_snapshot.py:44-59`, `backend/app/services/workspace_scanner.py:55-59`
- [x] Add file-size, total-size, and excluded-path limits for temporary snapshots.
- [x] Add tests with oversized files.

### [ ] P2-8 Keep broadcasts resilient to stale sockets

- Evidence: `backend/app/ws/manager.py:30-34`
- [x] Remove failed sockets during broadcast without aborting delivery to healthy clients.
- [x] Add a partial broadcast failure test.

### [ ] P2-9 Review frontend bundle size after correctness fixes

- Evidence: `npm run build` reports a `747.20 kB` main chunk.
- [x] Measure the largest imports.
- [x] Lazy-load heavy preview or editor features where appropriate.
- [x] Record the post-change bundle size.

---

## Recommended Execution Order

- [x] Phase 1: `P0-1`, `P0-2`, and `P1-9` together so cancellation and write completion have a trustworthy audit basis.
- [x] Phase 2: `P1-1`, `P1-2`, `P1-5`, and `P1-6` to close protocol and state-machine gaps.
- [x] Phase 3: `P1-3`, `P1-4`, and `P1-7` to stabilize shared state and recovery.
- [x] Phase 4: `P1-8` and the P2 reliability items.
- [x] Phase 5: Run full verification and update the implementation report.

## Required Verification

- [x] Run targeted regression tests after each item.
- [x] Run `cd backend && pytest -q`.
- [x] Run `cd frontend && npm run lint`.
- [x] Run `cd frontend && npm run build`.
- [x] Run `git diff --check`.
- [x] Run Alembic upgrade against a fresh temporary SQLite database.
- [x] Run a manual Mock-first group chat smoke test.
- [x] Verify stop generation against a deliberately blocked Agent execution.
- [x] Verify restart reconciliation for an active run and a paused run.
- [x] Update `docs/plans/M3_IMPLEMENTATION_REPORT.md`.
- [x] Append a completion entry to `DEVLOG.md`.

## Out Of Scope

- P2 product features such as deployment UI, mobile support, or PPT preview.
- Replacing the current Agent platforms.
- Removing `MockAdapter`.
- Unrelated frontend redesign.
