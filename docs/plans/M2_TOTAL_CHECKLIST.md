# M2 Chat Core Checklist

## Docs
- [x] `docs/plans/M2_TOTAL_PLAN.md` created.
- [x] `docs/plans/M2_TOTAL_CHECKLIST.md` created.
- [x] M2 submodule plan/checklists created.

## Implementation
- [x] Contract reviewed.
- [x] Backend tests written first.
- [x] Conversation list supports search and `lastMessage`.
- [x] New conversation modal supports single/group Agent selection.
- [x] Message input supports @ mention selection.
- [x] WebSocket handles Orchestrator status, thinking, errors, artifacts, and done events.
- [x] Rule-based Orchestrator dispatches mentioned Agents sequentially with MockAdapter.
- [x] Builtin Agents remain Mock-backed and user UI does not show `platformId`.

## Verification
- [x] Targeted M2 backend tests pass.
- [x] Backend suite passes.
- [x] Frontend lint passes.
- [x] Frontend build passes.
- [x] DEVLOG updated.
