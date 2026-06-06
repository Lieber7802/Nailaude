# M5 Vite HTML Preview Fix Plan

## Goal

Fix generated Vite project previews whose `index.html` renders blank because asset URLs resolve outside the conversation workspace preview route.

## Scope

- Backend preview service HTML responses for `/preview/{conversation_id}/*`.
- Frontend iframe preview source selection.
- Focused backend/frontend tests and DEVLOG.

## Contract Notes

- Existing `Artifact.previewUrl` remains the preview entry contract.
- No shared type, REST payload, or WebSocket payload shape changes.
- `/preview/{conversation_id}/{file_path}` remains the only browser preview route.

## Implementation Steps

1. Add failing tests for Vite-style `/assets/...` HTML under a nested build output such as `dist/index.html`.
2. Add a frontend helper so previewable HTML artifacts with `previewUrl` load via iframe `src`, preserving relative workspace assets.
3. Rewrite root-relative asset references in served HTML to the current preview directory.
4. Run targeted frontend and backend tests.

## Tests

- Backend preview test: `/preview/{conversation}/dist/index.html` rewrites `/assets/app.js` to `/preview/{conversation}/dist/assets/app.js`.
- Frontend helper test: HTML artifact with `previewUrl` uses `src`, not `srcDoc`.

## Out of Scope

- Running generated Vite dev servers.
- Building generated projects automatically.
- New dependencies.
