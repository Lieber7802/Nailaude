# M4 Artifact Preview Checklist

## Docs
- [x] Plan created or updated
- [x] Checklist created or updated
- [x] `AGENTS.md`, `API_SPEC.md`, `types.ts`, and `TASK_BREAKDOWN.md` reviewed

## Backend
- [x] Tests written first for preview route and file diff detection
- [x] File watcher detects created/modified/deleted files with `DiffData`
- [x] Artifact service persists webpage/code/diff artifacts from Agent events
- [x] Preview route serves raw files with traversal protection and CSP headers
- [x] WebSocket artifact events use the artifact service

## Frontend
- [x] CodeCard supports copy, line count, and compact code preview
- [x] DiffCard renders additions/deletions and changed lines
- [x] WebPreviewCard renders an iframe thumbnail and opens the right panel
- [x] PreviewPanel supports outputs, preview, code, and diff views

## Verification
- [x] Targeted M4 backend tests pass
- [x] Full backend tests pass
- [x] Frontend build passes
- [x] Backend syntax compile passes
- [x] DEVLOG updated
