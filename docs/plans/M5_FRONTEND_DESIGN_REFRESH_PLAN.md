# M5 Frontend Design Refresh Plan

## Goal

Refresh the Nailaude frontend visual system to match the provided Claude-inspired design reference while preserving the current chat, artifact, preview, and WebSocket behavior.

## Scope

- Frontend global CSS tokens, typography, surfaces, buttons, cards, chat stream, side panes, input, preview panel, and Markdown/code containers.
- Lightweight frontend style guard test for the core design tokens and reduced-gradient direction.
- Planning/checklist documentation and DEVLOG handoff notes.

## Contract Notes

- No backend API, WebSocket, adapter, or database contract changes are needed.
- No `packages/shared/types.ts` changes are needed.
- No new npm or pip dependencies are needed; typography uses Georgia/system fallbacks from the supplied design notes.

## Implementation Steps

1. Add a focused test that asserts the Claude-inspired palette and typography tokens exist in `frontend/src/index.css`.
2. Replace the current saturated orange/gradient-heavy UI tokens with warm parchment, ivory, terracotta, warm neutral, and ring-shadow tokens.
3. Restyle the existing shell, sidebar, chat, message, artifact, input, preview, Markdown, and modal-adjacent surfaces through CSS only where possible.
4. Run frontend tests and build.
5. Update checklist and DEVLOG.

## Tests

- `cd frontend && npm test`
- `cd frontend && npm run build`

## Out of Scope

- Reworking UX flows or component data contracts.
- Adding custom Anthropic fonts or remote font assets.
- P2 features such as deployment, mobile app work, or new preview capabilities.
