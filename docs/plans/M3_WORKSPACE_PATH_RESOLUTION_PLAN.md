# M3 Workspace Path Resolution Plan

## Goal

Fix group-chat completion cards that show `Workspace missing` after OpenCode successfully creates artifacts in a relative `workspaces/...` conversation directory.

## Scope

- Normalize backend services so relative `workspaces/...` paths resolve against the AgentHub repository root.
- Keep absolute paths and existing temporary test paths working as-is.
- Ensure ProjectState and workspace snapshot/audit logic use the same workspace root as ArtifactService.

## Contract Notes

- No REST, WebSocket, or shared TypeScript contract changes.
- `Conversation.workDir` remains the contract field used by frontend and backend.
- This is a backend path-resolution bug fix; agent roles and adapter selection are out of scope.

## Implementation Steps

1. Add regression tests for relative `workspaces/...` project state scanning and snapshot capture.
2. Introduce a shared resolver for `workspaces/...` paths in backend workspace services.
3. Reuse the resolver in ProjectState, GitInspector inputs, WorkspaceScanner, WorkspaceSnapshotService, and ArtifactService.
4. Verify target tests and update DEVLOG.

## Tests

- Project state should scan a repository-root `workspaces/<name>` directory when the conversation stores a relative workDir.
- Workspace snapshot/audit should capture files from that same relative workspace path.
- Existing absolute/temp workspace tests should remain green.

## Out of Scope

- Frontend UI changes.
- API/shared type changes.
- Creating or deleting user workspaces.
