# M2_2 New Conversation Modal Plan

## Goal

Create single or group conversations from the UI.

## Scope

- Modal form with type, title, Agent selection, and workDir.
- Single chat uses one participant; group chat supports multiple participants.
- Created conversation becomes active.

## Contract Notes

- Use existing `POST /conversations`.
- Keep backend workDir safety validation under `workspaces/`.

## Implementation Steps

- Add `NewConversationModal`.
- Wire modal state and create action in Workspace.
- Validate participant ids on the backend.

## Tests

- Frontend build.
- Backend API tests cover participant validation through create flow.

## Out of Scope

- Agent CRUD and project directory picker.
