# M4 UI Optimization Plan

## Goal

Polish the M4 chat and preview experience so artifacts stay compact in the chat stream, the right preview panel becomes the only preview surface, active runs can be stopped, side panes can be resized/collapsed, Shared context is hidden from the chat stream, and agent replies render Markdown.

This follow-up also fixes tested UI issues: collapse controls should sit in the annotated divider-control area, chat code-block Markdown should render correctly, chat timestamps should match the user's current local time, and the `@代理` / `附件` input tools should be usable.

This second follow-up expands Markdown rendering to a full GFM engine with sanitized HTML, moves diff artifacts out of the Outputs tab into a dedicated real-time Changes list, and orders chat artifact cards so newly created files appear before edited/changed files.

This third follow-up simplifies chat artifact cards to Codex-style file rows, localizes user-facing "代理" wording to "智能体", and fixes `stop_generation` so cancellation applies to the entire current chat run, including queued/planning windows before agent execution starts.

This fourth follow-up fixes collaboration state and status-card readability: the collaboration panel now only shows intelligent agents involved in the current run, the main intelligent-agent card is localized and uses checklist-style task rows, and DeepSeek summary failures degrade quietly instead of appearing as user-facing warnings.

This fifth follow-up improves HTML preview ergonomics: fullscreen preview now lets the browser preview fill the available panel height, and the internal viewport zoom supports broad slider-based scaling instead of only a few fixed steps.

## Scope

- Frontend artifact cards: show summary metadata and actions only, with no inline code, diff, Markdown, or iframe preview.
- Frontend chat input/header: expose a stop-generation control when a run is active.
- Frontend layout: support left conversation pane and right preview pane resizing and collapse.
- Frontend messages: render Markdown blocks in reply content.
- Frontend message timestamps: normalize backend UTC timestamps and browser-local optimistic timestamps into the user's local display time.
- Frontend input tools: make `@代理` open the mention selector and make `附件` open a file picker with selected-file chips and text handoff.
- Frontend Markdown preview: use `marked` for GFM syntax and `DOMPurify` for sanitized rendering.
- Frontend preview changes: aggregate all diff artifacts in the right-side Changes tab, collapsed by default.
- Frontend message artifacts: sort created outputs before diff/change cards.
- Frontend message artifacts: hide status labels plus copy/external-open actions and keep only right-side preview/open actions.
- Frontend copy: replace user-facing "代理" wording with "智能体".
- Backend WebSocket cancellation: make `stop_generation` cancel queued runs and remember cancellation requested before runtime execution starts.
- Frontend collaboration status: show only current-task/thinking intelligent agents once a run starts.
- Frontend orchestrator card: localize labels and render task rows as a checklist with running/completed icons.
- Backend project/team summary: use deterministic fallback behavior when DeepSeek summarization fails and avoid user-facing summary failure warnings.
- Frontend HTML preview: fill available preview height in fullscreen and regular preview mode.
- Frontend preview zoom: support free scaling from 25% to 300% with slider and fine step buttons.
- Docs/tests: add focused tests for Markdown parsing and artifact card presentation helpers.

## Contract Notes

- No `packages/shared/types.ts` change is needed.
- Existing WebSocket `stop_generation` message shape is used as-is; its backend semantics now cover queued, planning, and executing run states.
- Existing backend preview and artifact contracts remain unchanged.
- `marked` and `DOMPurify` are direct frontend dependencies because full Markdown/GFM coverage and sanitized HTML rendering are required.

## Implementation Steps

1. Add tests for chat Markdown parsing and artifact card presentation helpers.
2. Hide the TeamBoard/Shared context panel from `ChatArea`.
3. Convert code/diff/web artifact cards into compact cards with copy/open actions only.
4. Add stop-generation button wiring through `Workspace` and `MessageInput`.
5. Add UI store state and `Layout` drag handles for pane width/collapse.
6. Run frontend tests/build and update checklist plus DEVLOG.
7. Add follow-up tests for indented/tilde code fences, timestamp normalization, and attachment summary formatting.
8. Move collapse buttons to the divider-control area and complete input tool interactions.
9. Replace hand-written Markdown rendering with sanitized GFM HTML rendering.
10. Split preview Outputs and Changes data sources so diff artifacts only appear in Changes.
11. Sort chat artifact cards by created outputs first and changed files last.
12. Simplify chat cards to one right-side preview/open action.
13. Update visible UI copy from "代理" to "智能体".
14. Extend backend cancellation to queued and pre-execution run states.
15. Make collaboration status dynamic and scoped to the current task agents.
16. Localize the main intelligent-agent status card and render tasks as a checklist.
17. Suppress DeepSeek summary failure noise and keep deterministic state updates.
18. Make HTML preview viewport fill the preview stage height.
19. Replace narrow zoom buttons with broad slider-based preview scaling.

## Tests

- `cd frontend && npm test`
- `cd frontend && npm run build`

## Out of Scope

- Force-killing planner LLM requests during planning; cancellation is recorded and prevents later agent execution.
- New dependencies.
- Backend file upload/persistence for attachments; the MVP input records selected-file names and sizes in the sent message text.
- P2 preview features such as applying diffs or version history switching.
