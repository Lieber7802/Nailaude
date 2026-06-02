# M4 Preview Controls Polish Plan

## Goal

Polish the webpage preview controls so viewport switching is clear and contained, and the fullscreen action behaves like a real fullscreen/exit-fullscreen toggle.

## Scope

- Frontend right preview panel only.
- Viewport and zoom control labels/layout in `IframePreview`.
- Fullscreen toggle state, icon, label, and fallback overlay behavior in `PreviewPanel`.
- Focused frontend regression tests and build verification.

## Contract Notes

- No shared type, REST, WebSocket, or backend contract changes are needed.
- Existing preview artifact data and `previewUrl` behavior remain unchanged.

## Implementation Steps

1. Add failing frontend tests for viewport option labels and fullscreen action labels.
2. Reuse tested preview-control metadata in `IframePreview` and `PreviewPanel`.
3. Replace ambiguous icon-only viewport controls with labeled segmented controls.
4. Use browser Fullscreen API where available, with a full-viewport CSS fallback.
5. Run frontend tests, build, and diff checks.

## Tests

- `cd frontend && npm test`
- `cd frontend && npm run build`
- `git diff --check`

## Out of Scope

- Backend preview service changes.
- New dependencies.
- Persisting per-artifact viewport or zoom preferences.
