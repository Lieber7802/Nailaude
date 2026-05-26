# M2 Chat Core Review Report

> Date: 2026-05-26  
> Scope: M2 chat core implementation, including conversation list, new conversation modal, @ mention routing, message runtime UI, WebSocket dispatch, and rule-based Orchestrator.  
> Review mode: strict code review. This document lists optimization and bug-fix tasks for the implementation Agent.

## Summary

M2 has a usable Mock-first chat loop. Backend tests pass and frontend production build succeeds, so there is no P0 blocker found in the current implementation.

However, several runtime edge cases can produce incorrect task state, cross-conversation Agent dispatch, stale UI state, or contract drift. These should be fixed before using M2 as the base for real Adapter/LLM integration.

## Verification Snapshot

- `pytest -q` -> 11 passed
- `pytest backend/tests/test_m2_chat_core.py -q` -> 3 passed
- `cd frontend && npm run build` -> passed
- `cd frontend && npm run lint` -> failed

Lint failures:

- `frontend/src/stores/messageStore.ts:82` unused `_removed`
- `frontend/src/stores/messageStore.ts:97` unused `_removed`
- `frontend/src/utils/diff.ts:4` unused `_diffText`
- `frontend/src/utils/diff.ts:9` unused `_original`
- `frontend/src/utils/diff.ts:9` unused `_diffText`

## P1 Issues

### M2-REVIEW-01: Failed Agent stream is reported as completed

Priority: P1  
Area: WebSocket orchestration, runtime status  
Files:

- `backend/app/ws/handlers.py`
- `frontend/src/hooks/useWebSocket.ts`
- `frontend/src/stores/uiStore.ts`

Current behavior:

- `handle_send_message()` always marks a task as `completed` after `stream_agent_task()` returns.
- `stream_agent_task()` catches exceptions internally, persists partial content, emits an `error`, and then returns text.
- Because the exception is swallowed, the Orchestrator cannot distinguish success from failure.
- Frontend clears `thinkingAgents` only on `message_done`. If an error happens before `message_done`, the runtime banner may keep showing the Agent as thinking.

Why this matters:

- The user sees a failed Agent task as completed.
- The runtime UI can get stuck in an active/thinking state.
- Real Adapter integration will make this much more common because external process/API failures are expected.

Suggested fix:

- Make `stream_agent_task()` return a structured result such as:

```python
{
    "status": "success" | "failed" | "partial",
    "content": "...",
    "error": "...",
}
```

- In `handle_send_message()`, mark task status from that result:
  - `success` -> `completed`
  - `failed` or `partial` -> `failed` for M2, or introduce `partial` only if the shared contract is updated.
- On failure, emit an event that lets the frontend clear thinking state. Options:
  - include `agentName` / `agentId` in the existing `error` payload, then clear by Agent;
  - or emit `message_done` with error metadata;
  - or add a dedicated terminal event, but only with `packages/shared/types.ts` and `docs/API_SPEC.md` updated together.
- Add a backend test with an adapter that raises mid-stream and assert final `orchestrator_status.tasks[n].status == "failed"`.
- Add a frontend store/unit-level test if test infra exists, or manual QA case: runtime banner must clear after error.

Acceptance criteria:

- A failing Agent task is never marked `completed`.
- Frontend thinking state is cleared after both success and failure.
- The failed task carries a useful error summary in Orchestrator status or runtime error UI.

### M2-REVIEW-02: WebSocket mentions can dispatch Agents outside the conversation

Priority: P1  
Area: backend authorization/dispatch boundary  
Files:

- `backend/app/ws/handlers.py`
- `backend/tests/test_m2_chat_core.py`

Current behavior:

- `resolve_dispatch_agents()` trusts `payload.mentions`.
- It queries all Agents by mentioned IDs.
- It does not verify that mentioned Agent IDs are included in `conversation.participant_ids`.

Why this matters:

- The frontend mention selector normally limits choices, but WebSocket payloads can be crafted manually.
- A conversation can invoke an Agent that was not added to that conversation.
- This breaks the Conversation module boundary and will be risky once platform-backed Agents have permissions or workspace-specific context.

Suggested fix:

- In `resolve_dispatch_agents()`, restrict mentioned IDs to `conversation.participant_ids`.
- If a mention references a non-participant Agent, prefer returning a recoverable error such as `Mentioned agent is not part of this conversation`.
- Keep fallback behavior only within the participant list.
- Add test:
  - create two Agents and a conversation with only Agent A;
  - send WebSocket message mentioning Agent B;
  - assert an error event and no Agent B message is persisted.

Acceptance criteria:

- Mentioned Agents must be conversation participants.
- Non-participant mentions are rejected clearly.
- Persisted agent messages only belong to participants.

### M2-REVIEW-03: Empty-participant conversations fall back to a global Agent

Priority: P1  
Area: conversation creation, dispatch safety, frontend fallback  
Files:

- `backend/app/api/conversations.py`
- `backend/app/ws/handlers.py`
- `frontend/src/pages/Workspace.tsx`
- `frontend/src/components/chat/ChatArea.tsx`
- `frontend/src/components/chat/NewConversationModal.tsx`

Current behavior:

- `validate_participants()` returns successfully when `participant_ids` is empty.
- `resolve_dispatch_agents()` falls back to the first global Agent if a conversation has no participants.
- Frontend also falls back to all Agents in message input when the current conversation has no participant Agents.

Why this matters:

- A malformed or API-created conversation with no participants can still dispatch work.
- The UI and backend may select different fallback Agents.
- This makes dispatch behavior implicit and hard to reason about.

Suggested fix:

- Enforce at least one participant on `ConversationCreate`.
- For `ConversationUpdate`, reject an empty `participantIds` list unless there is a deliberate product decision to support "draft" conversations.
- Remove backend global Agent fallback from `resolve_dispatch_agents()`.
- In frontend, do not expose all Agents for a conversation with empty participants. Show a disabled input or a recoverable UI error.
- Add tests:
  - `POST /conversations` with empty `participantIds` returns validation error.
  - WebSocket send on an empty-participant conversation returns `Agent not found` or a clearer conversation configuration error.

Acceptance criteria:

- Every active conversation has at least one participant.
- WebSocket dispatch never silently picks a global Agent.
- UI behavior matches backend behavior.

## P2 Issues

### M2-REVIEW-04: REST message fallback contract does not match API spec

Priority: P2  
Area: API contract consistency  
Files:

- `backend/app/api/messages.py`
- `docs/API_SPEC.md`
- `packages/shared/types.ts` if WS/REST contracts change

Current behavior:

- API spec describes `POST /conversations/{id}/messages` as a REST fallback that triggers Orchestrator + Agent execution, with actual replies pushed over WebSocket.
- Implementation only persists the user message and returns it.

Why this matters:

- Consumers who use REST fallback will not receive Agent replies.
- The code and docs disagree, which is especially confusing for future Adapter work.

Suggested fix options:

Option A, align implementation with docs:

- Reuse the same orchestration path as WebSocket send.
- This may require a background task or event manager design because REST cannot stream directly.
- Define what happens when no WebSocket client is connected.

Option B, align docs with implementation for M2:

- Explicitly document REST as "persist user message only" for debug/basic fallback.
- Keep WebSocket as the only execution path for M2.

Recommended for M2:

- Choose Option B unless execution fallback is required for demo acceptance.
- Add a note in `docs/API_SPEC.md` and M2 plan/checklist that REST fallback does not invoke Agents in M2.

Acceptance criteria:

- API docs and backend behavior describe the same fallback semantics.
- Tests assert the chosen behavior.

### M2-REVIEW-05: @ mention extraction can over-match Agent names

Priority: P2  
Area: frontend mention parsing  
Files:

- `frontend/src/services/api.ts`
- `frontend/src/components/chat/MessageInput.tsx`
- `frontend/src/components/chat/MentionSelector.tsx`

Current behavior:

- `extractMentions()` uses `content.includes("@${agent.name}")`.
- If Agent names overlap, such as `小马` and `小马哥`, `@小马哥` can match both Agents.
- Mentions are reconstructed from text instead of preserving the selected Agent IDs.

Why this matters:

- User intent can be routed to the wrong Agent.
- The issue becomes harder to detect when group conversations have many custom Agents.

Suggested fix:

- Prefer preserving selected mention metadata in `MessageInput` state.
- When a user selects an Agent from `MentionSelector`, store `{ agentId, agentName, start, end }` or a lightweight token map.
- On send, emit the stored selected mentions rather than re-parsing all text with `includes`.
- If keeping text parsing for M2, sort Agent names by length descending and use a boundary-aware regex.

Acceptance criteria:

- Selecting `@小马哥` does not mention `小马`.
- Manually typed mentions have deterministic behavior.
- Duplicate mentions are de-duplicated by `agentId`.

### M2-REVIEW-06: Conversation list lastMessage and ordering are stale after sending

Priority: P2  
Area: frontend state synchronization  
Files:

- `frontend/src/pages/Workspace.tsx`
- `frontend/src/stores/conversationStore.ts`
- `frontend/src/hooks/useWebSocket.ts`

Current behavior:

- Conversation list is refreshed by `conversationApi.list()` on initial/search effect.
- Sending a message updates only `messageStore`.
- `lastMessage` and list ordering are not updated after `user_message`, `text_delta`, or `message_done`.

Why this matters:

- Sidebar can show an old last message after active chat receives new messages.
- Conversation ordering may not reflect recent activity until refresh/search.
- This weakens M2's "IM style" experience.

Suggested fix:

- Add a conversation store action such as `touchConversation(id, lastMessage, updatedAt)`.
- Call it when:
  - optimistic user message is added;
  - persisted `user_message` arrives;
  - `message_done` arrives for Agent response.
- Keep formatting consistent with backend `format_last_message()`, or centralize the display formatter on the frontend.
- Optionally refetch the first conversation page after `message_done` if simpler for M2.

Acceptance criteria:

- Sidebar last message updates immediately after user send.
- Sidebar last message updates again after Agent completion.
- Active conversation moves to the top after new activity.

### M2-REVIEW-07: Runtime error is sticky until reconnect/reset

Priority: P2  
Area: frontend runtime state  
Files:

- `frontend/src/hooks/useWebSocket.ts`
- `frontend/src/stores/uiStore.ts`
- `frontend/src/components/chat/ChatArea.tsx`

Current behavior:

- `setRuntimeError()` sets an error banner.
- Successful later events do not clear it.
- `RuntimeBanner` returns early when `runtime.error` exists, so Orchestrator status and thinking tags are hidden while error is sticky.

Why this matters:

- A recoverable error can hide subsequent healthy progress.
- Users may think the conversation is still broken after a later successful send.

Suggested fix:

- Clear `runtime.error` when a new `send_message` starts, or when `user_message` / `orchestrator_status: dispatching` is received.
- Consider showing error and current status together instead of returning early.
- Keep unrecoverable errors visible only until next user action.

Acceptance criteria:

- Sending a new message clears previous recoverable error state.
- Runtime status remains visible even if there was a past error.

## P3 Issues

### M2-REVIEW-08: Frontend lint is failing

Priority: P3  
Area: frontend hygiene / CI readiness  
Files:

- `frontend/src/stores/messageStore.ts`
- `frontend/src/utils/diff.ts`

Current behavior:

- `npm run lint` fails on unused destructured variables and unused placeholder parameters.

Why this matters:

- Build passes, but CI should not accept a known red lint state.
- The M2 checklist says frontend build passes, but lint should be part of completion once CI adds it.

Suggested fix:

- Replace unused destructured variables with an omit helper or delete through object copy without binding unused names.
- For placeholder functions in `frontend/src/utils/diff.ts`, either implement the logic, remove unused parameters, or intentionally mark them with an ESLint-compatible convention if configured.

Acceptance criteria:

- `cd frontend && npm run lint` passes.

### M2-REVIEW-09: Dead helper remains after dispatch refactor

Priority: P3  
Area: backend cleanup  
Files:

- `backend/app/ws/handlers.py`

Current behavior:

- `resolve_agent()` remains in the file but is no longer referenced.

Why this matters:

- Low risk, but it can confuse future maintainers because there are now two resolution paths.

Suggested fix:

- Remove `resolve_agent()` if no longer used.
- Keep only `resolve_dispatch_agents()` after adding participant-boundary checks.

Acceptance criteria:

- No unused dispatch helper remains.
- Tests still pass.

## Suggested Fix Order

1. Fix `M2-REVIEW-02` and `M2-REVIEW-03` first to enforce conversation/Agent boundaries.
2. Fix `M2-REVIEW-01` next so runtime status is truthful under failures.
3. Resolve `M2-REVIEW-04` by choosing and documenting REST fallback semantics.
4. Fix `M2-REVIEW-05` and `M2-REVIEW-06` for user-facing M2 quality.
5. Fix `M2-REVIEW-07` through `M2-REVIEW-09` as cleanup and CI hardening.

## Recommended Regression Tests

Backend:

- `test_ws_rejects_mentioned_agent_not_in_conversation`
- `test_create_conversation_rejects_empty_participants`
- `test_ws_marks_task_failed_when_adapter_raises`
- `test_rest_message_fallback_matches_documented_behavior`

Frontend:

- `extractMentions` or replacement mention-token logic does not over-match overlapping names.
- Runtime store clears thinking on error terminal path.
- Conversation store updates `lastMessage` and ordering after new messages.

Manual QA:

- Create a single-Agent conversation, send without @, confirm only that Agent runs.
- Create a group conversation, mention two Agents, confirm sequential status transitions.
- Force/reproduce an adapter error, confirm task is failed and thinking state clears.
- Send another message after an error, confirm stale error banner does not hide new runtime status.

## Notes for Implementation Agent

- Keep `MockAdapter` as the permanent fallback.
- Do not introduce LLM/CLI Adapter work while fixing this review unless explicitly requested.
- If any WebSocket payload shape changes, update both `packages/shared/types.ts` and `docs/API_SPEC.md` in the same change.
- Prefer adding failing tests before implementation for each P1/P2 item.
