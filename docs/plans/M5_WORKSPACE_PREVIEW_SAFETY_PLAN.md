# M5 Workspace Preview Safety Plan

## Goal

Improve conversation workspace naming UX and prevent generated preview projects from hijacking the AgentHub frontend dev port or opening browser windows automatically.

## Scope

- Frontend new conversation modal copy and work directory submission normalization.
- Backend conversation `workDir` normalization and workspace directory creation.
- OpenCode and Codex adapter prompts for generated app dev-server safety.
- Focused frontend/backend tests and smoke verification.

## Contract Notes

- `CreateConversationDTO.workDir` remains a string, so no shared type shape change is required.
- Backend accepts empty `workDir` for automatic unique workspace creation.
- Backend now accepts bare workspace names and persists them as `workspaces/<name>`.
- Existing `workspaces/<name>` and validated workspace-root paths remain supported.

## Implementation Steps

1. Add tests for bare workspace names, generated-project prompt safety, and frontend work directory normalization.
2. Implement backend normalization helpers and use them for create/update conversation flows.
3. Update new conversation modal label/placeholder and submit normalized workspace names.
4. Add adapter prompt constraints to avoid `server.open`, `open: true`, fixed AgentHub ports, and commands that auto-open browsers.
5. Run targeted tests, broader frontend/backend verification, and record DEVLOG.

## Tests

- Backend API tests for `workDir: "todo-app"` -> `workspaces/todo-app`.
- Backend adapter tests for OpenCode/Codex prompt safety constraints.
- Frontend node tests for workspace-name normalization.
- Frontend build and backend targeted pytest suite.

## Out of Scope

- Full production preview server orchestration.
- Live browser E2E automation for generated apps.
- New dependencies.
