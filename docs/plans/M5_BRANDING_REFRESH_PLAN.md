# M5 Branding Refresh Plan

## Goal

Replace the app branding with the Nailaude logo image and update the visible product name and browser chrome title to Nailaude.

## Scope

- Frontend sidebar header branding.
- Browser title and favicon.
- Static logo asset placement under `frontend/public/`.
- No API, WebSocket, shared type, backend, or dependency changes.

## Contract Notes

- `docs/API_SPEC.md` and `packages/shared/types.ts` were reviewed.
- This is a visual-only frontend change and does not alter request/response payloads or shared contracts.

## Implementation Steps

1. Add the provided `nailaude_logo.png` to the Vite public assets.
2. Replace the Ant Design home icon brand mark with an image element.
3. Change the displayed product name to `Nailaude`.
4. Adjust brand CSS so the image is consistently sized and cropped in the sidebar.
5. Point the browser favicon and title to the Nailaude brand.

## Tests

- Run the frontend production build.
- Run a targeted source check for the old `Nailaude` sidebar brand text.
- Verify the browser title and favicon link in the running app.

## Out of Scope

- Renaming internal packages, API documents, database values, or product references outside the requested sidebar header.
- Renaming internal packages, API documents, database values, or product references outside the requested branding surfaces.
