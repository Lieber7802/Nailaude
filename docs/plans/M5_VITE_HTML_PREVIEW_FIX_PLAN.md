# M5 Vite HTML Preview Fix Plan

## Goal

Fix generated Vite project previews whose source `index.html` renders blank because the page depends on Vite's dev server transforms instead of browser-native static HTML execution.

## Scope

- Backend preview service HTML responses for `/preview/{conversation_id}/*`.
- Frontend iframe preview source selection.
- Backend-managed Vite dev server proxy for workspace source projects.
- Preview CSP for generated static pages that load CDN runtimes such as React/Babel.
- Focused backend/frontend tests and DEVLOG.

## Contract Notes

- Existing `Artifact.previewUrl` remains the preview entry contract.
- No shared type, REST payload, or WebSocket payload shape changes.
- `/preview/{conversation_id}/{file_path}` remains the only browser preview route.
- Vite dev-server proxying is an implementation detail behind the existing preview route.
- Preview responses keep iframe isolation but allow HTTPS CDN resources and Babel standalone's runtime eval needs.

## Implementation Steps

1. Keep existing static build regression coverage for Vite-style `/assets/...` HTML under `dist/index.html`.
2. Detect Vite source workspaces from `package.json`.
3. Start and cache `npm run dev -- --host 127.0.0.1 --port <free-port>` for source previews.
4. Proxy Vite source, transformed JS/CSS, `/@vite/*`, and `/node_modules/.vite/*` requests through `/preview/{conversation_id}/*`.
5. Rewrite root-absolute URLs in proxied text responses back under `/preview/{conversation_id}`.
6. Stop spawned dev servers during FastAPI lifespan shutdown.
7. Allow HTTPS scripts/styles/fonts/images in preview CSP and include `unsafe-eval` for static Babel previews.
8. Run targeted frontend and backend tests.

## Tests

- Backend preview test: `/preview/{conversation}/dist/index.html` rewrites `/assets/app.js` to `/preview/{conversation}/dist/assets/app.js`.
- Backend preview test: `/preview/{conversation}/index.html` for a Vite source project uses the dev-server proxy and rewrites `/src/main.tsx`.
- Backend preview test: dev-server-only paths such as `/@vite/client` proxy before static file existence checks.
- Backend preview test: generated CDN static pages receive CSP allowing `https:` resources and `unsafe-eval`.
- Frontend helper test: HTML artifact with `previewUrl` uses `src`, not `srcDoc`.

## Out of Scope

- Building generated projects automatically.
- New dependencies.
