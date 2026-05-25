# M2 Chat Core Plan

## Goal

Complete the demo-first M2 chat core: searchable conversations, real conversation creation, @ mention routing, improved message stream UI, and rule-based Mock Orchestrator dispatch.

## Scope

- M2_1: conversation list search, last message preview, switching, and deletion.
- M2_2: new conversation modal with Agent selection and workspace path input.
- M2_3: @ mention selector in the message composer.
- M2_4: message metadata, runtime status, thinking, and error display.
- M2_5: rule-based OrchestratorService and sequential MockAdapter execution.
- M2_6: builtin Agent seed remains three Mock-backed roles.

## Contract Notes

- Reuse current REST and WebSocket contracts from `docs/API_SPEC.md` and `packages/shared/types.ts`.
- Do not add LLM decision-making, CLI adapters, Agent CRUD UI, or M4 preview enhancements.
- Keep all builtin Agents bound to `mock` for M2.
- REST `POST /conversations/{id}/messages` remains a debug/basic fallback in M2: it persists the user message only and does not invoke Orchestrator.

## Implementation Steps

- Add backend tests for conversation `lastMessage`, Orchestrator planning, and multi-Agent WebSocket dispatch.
- Implement `OrchestratorService.build_dispatch_plan()` as a sequential rule router.
- Update WebSocket handling to emit `orchestrator_status` and run each selected Mock Agent.
- Update frontend API typing to use shared type contracts through a thin wrapper.
- Build ConversationList, NewConversationModal, MentionSelector, runtime status, and improved MessageBubble.
- Verify backend pytest and frontend production build.

## Tests

- `cd backend && pytest -q`
- `cd frontend && npm run build`

## Out of Scope

- Fireworks/Volcano/LLMProvider integration.
- OpenCode/Codex CLI process management.
- Full context engineering, ProjectState, and TeamBoard mutation.
- Monaco/Diff/iframe preview upgrades.
