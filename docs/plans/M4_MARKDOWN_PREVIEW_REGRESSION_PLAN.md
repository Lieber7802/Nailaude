# M4 Markdown Preview Regression Plan

## Goal

Fix Markdown review artifacts so they preview as rendered documents in both the chat artifact card and the right preview panel, while keeping long file names from wrapping the preview panel tabs.

## Scope

- Frontend Markdown detection and lightweight rendered preview for `.md` / `.markdown` artifact files.
- Chat `CodeCard` rendering for Markdown artifacts.
- Right `PreviewPanel` preview tab behavior and header filename layout.
- Frontend regression tests and build verification.

## Contract Notes

- No shared type, REST, WebSocket, or backend preview contract changes are needed.
- Existing `Artifact.files[].language`, `Artifact.files[].name`, and `Artifact.files[].content` already carry Markdown artifacts.

## Implementation Steps

1. Add failing frontend tests for Markdown artifact detection and preview mode selection.
2. Implement reusable Markdown preview helpers and a rendered Markdown component.
3. Route Markdown artifacts to rendered preview in chat cards and the right preview tab.
4. Constrain right-panel toolbar filename overflow so tabs stay on one line.
5. Run targeted frontend tests and `npm run build`.

## Tests

- `cd frontend && npm test`
- `cd frontend && npm run build`

## Out of Scope

- Adding Markdown parser dependencies.
- Editing backend artifact generation.
- Adding full GitHub-Flavored Markdown parity.
