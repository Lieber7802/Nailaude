# M4 Artifact Preview Plan

## Goal

Complete the M4 artifact and preview MVP owned by 洋芋: generated code/webpage/diff artifacts render in chat, open in the right preview panel, and static webpage files are served by the backend preview route.

## Scope

- Backend `FileWatcherService`: track project directory snapshots and produce file change records with `DiffData`.
- Backend `ArtifactService`: normalize `AgentEvent(file_created/file_modified)` payloads, persist `Artifact` rows, generate preview URLs for HTML artifacts, and compute diff artifacts.
- Backend Preview API: serve raw files from conversation `workDir` at `/preview/{conversation_id}/{filepath}` with content type and CSP headers.
- WebSocket integration: use `ArtifactService` for artifact event persistence and push `artifact` payloads aligned with `API_SPEC.md`.
- Frontend cards: route `code`, `webpage`, and `diff` artifacts to purpose-built cards with copy/open actions and readable summaries.
- Frontend right panel: provide output list, iframe preview, read-only code editor, and diff viewer tabs.

## Contract Notes

- No `packages/shared/types.ts` change is needed; existing `Artifact`, `DiffData`, `WSArtifact`, and `/preview` contract already cover M4.
- `/preview/{conversation_id}/*` must not be wrapped in `ApiResponse`.
- M5 items remain out of scope: one-click apply diff, version history switching, and multi-file project preview routing beyond direct static file serving.

## Implementation Steps

1. Add failing backend tests for Mock artifact preview URL, raw preview file serving, and file watcher diff detection.
2. Implement artifact diff/normalization helpers and persist artifacts through the service.
3. Implement preview path resolution with traversal protection and CSP headers.
4. Wire the WebSocket artifact path through `ArtifactService`.
5. Replace placeholder frontend cards/viewers with typed implementations and update `MessageBubble` rendering.
6. Run targeted backend tests, full backend tests, and frontend build.

## Tests

- `cd backend && python -m pytest -q tests/test_m4_artifact_preview.py`
- `cd backend && python -m pytest -q`
- `cd frontend && npm run build`

## Out of Scope

- Adding new npm/pip dependencies.
- Editing shared contracts.
- Implementing M5 version history or applying patches back to the workspace.
