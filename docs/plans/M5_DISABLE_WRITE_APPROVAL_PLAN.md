# M5 Disable Write Approval Plan

## Goal

Remove Nailaude's elevated write approval gate so workspace-bound coding tasks run without showing the "Allow execution" approval card.

## Scope

- Backend WebSocket Orchestrator approval trigger.
- Regression tests for risky write plans.
- API documentation note for the approval message behavior.
- DEVLOG handoff entry.

## Contract Notes

- `packages/shared/types.ts` remains unchanged for backward compatibility with existing frontend code and persisted snapshots.
- The backend should no longer emit `orchestrator_approval_required` for write task risk hints.
- Existing CLI adapters already run non-interactively; this change only removes Nailaude's own Orchestrator approval pause.

## Implementation Steps

1. Replace approval-focused WebSocket tests with direct-execution regression coverage.
2. Remove the risk-hint conditions from `elevated_write_approval_reason`.
3. Update API documentation to mark approval messages as retained but not emitted by current policy.
4. Append DEVLOG with changed files, tests, and residual risk.

## Tests

- Targeted backend WebSocket interaction tests.
- Focused helper test for risky write tasks returning no approval reason.

## Out of Scope

- Removing shared protocol types or frontend approval card code.
- Changing Codex/OpenCode CLI permission flags.
- Adding a broader permission system.
