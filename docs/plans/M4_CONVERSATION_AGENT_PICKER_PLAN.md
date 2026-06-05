# M4 Conversation Agent Picker Plan

## Goal

Separate the two agent add flows in the workspace UI:
- The sidebar agent plus creates a new custom Agent.
- The chat header add action adds existing Agents to the current conversation.

## Scope

- Frontend workspace interactions.
- Existing REST conversation update contract.
- Focused UI helper tests.

## Contract Notes

- Use existing `PATCH /api/v1/conversations/{id}` with `participantIds`.
- Do not change shared types or backend payload shapes.
- Do not expose platform IDs in ordinary conversation add UI.

## Implementation Steps

1. Add a conversation update API client method.
2. Add local store support for replacing an updated conversation.
3. Add a modal for selecting existing Agents that are not already in the current conversation.
4. Wire chat header add action to the new modal.
5. Keep the sidebar agent plus wired to custom Agent creation.

## Tests

- Unit test candidate filtering for add-to-conversation.
- Unit test participant ID merging without duplicates.
- Run frontend tests and build.

## Out of Scope

- Removing Agents from conversations.
- Backend API contract changes.
- Agent editing or deletion.
