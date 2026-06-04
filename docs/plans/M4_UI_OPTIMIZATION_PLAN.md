# M4 UI Optimization Plan

## Goal

Polish the M4 chat and preview experience so artifacts stay compact in the chat stream, the right preview panel becomes the only preview surface, active runs can be stopped, side panes can be resized/collapsed, Shared context is hidden from the chat stream, and agent replies render Markdown.

This follow-up also fixes tested UI issues: collapse controls should sit in the annotated divider-control area, chat code-block Markdown should render correctly, chat timestamps should match the user's current local time, and the `@代理` / `附件` input tools should be usable.

## Scope

- Frontend artifact cards: show summary metadata and actions only, with no inline code, diff, Markdown, or iframe preview.
- Frontend chat input/header: expose a stop-generation control when a run is active.
- Frontend layout: support left conversation pane and right preview pane resizing and collapse.
- Frontend messages: render Markdown blocks in reply content.
- Frontend message timestamps: normalize backend UTC timestamps and browser-local optimistic timestamps into the user's local display time.
- Frontend input tools: make `@代理` open the mention selector and make `附件` open a file picker with selected-file chips and text handoff.
- Docs/tests: add focused tests for Markdown parsing and artifact card presentation helpers.

## Contract Notes

- No `packages/shared/types.ts` change is needed.
- Existing WebSocket `stop_generation` is used as-is.
- Existing backend preview and artifact contracts remain unchanged.

## Implementation Steps

1. Add tests for chat Markdown parsing and artifact card presentation helpers.
2. Hide the TeamBoard/Shared context panel from `ChatArea`.
3. Convert code/diff/web artifact cards into compact cards with copy/open actions only.
4. Add stop-generation button wiring through `Workspace` and `MessageInput`.
5. Add UI store state and `Layout` drag handles for pane width/collapse.
6. Run frontend tests/build and update checklist plus DEVLOG.
7. Add follow-up tests for indented/tilde code fences, timestamp normalization, and attachment summary formatting.
8. Move collapse buttons to the divider-control area and complete input tool interactions.

## Tests

- `cd frontend && npm test`
- `cd frontend && npm run build`

## Out of Scope

- Backend cancellation semantics beyond existing `stop_generation`.
- New dependencies.
- Backend file upload/persistence for attachments; the MVP input records selected-file names and sizes in the sent message text.
- P2 preview features such as applying diffs or version history switching.
