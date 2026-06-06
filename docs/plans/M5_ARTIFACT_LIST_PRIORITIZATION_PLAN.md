# M5 Artifact List Prioritization Plan

## Goal

Make Code Artisan artifact output readable when a complex project generates many files: chat messages should show only the three most useful artifact cards by default, allow users to expand the full list, and prioritize previewable outputs such as HTML pages and README/Markdown documents above ordinary source files.

## Research Findings

- This can be implemented stably in the frontend without changing REST, WebSocket, backend persistence, or `packages/shared/types.ts`.
- Current `MessageBubble` already merges persisted `message.artifacts` with live `artifactStore` entries and renders through `getOrderedMessageArtifacts()` plus `getVisibleMessageArtifacts()`.
- Current collapse behavior exists, but `MESSAGE_ARTIFACT_COLLAPSE_LIMIT` is `5`; the requested behavior is `3`.
- Current message ordering puts generic created/code artifacts before webpage artifacts and diff artifacts last. It does not yet prioritize HTML/README/Markdown preview targets.
- Existing helpers already recognize Markdown files through `isMarkdownFile()`, and HTML recognition exists in `markdownPreview.ts` as `isHtmlFile()`, so previewability can be detected with shared frontend utility logic.
- Existing `frontend/tests/artifactCard.test.mjs` covers artifact card presentation, output/diff splitting, ordering, and collapse. The safest path is to extend these pure logic tests before changing UI behavior.

## Scope

- Frontend artifact list logic in `frontend/src/utils/artifactCard.ts`.
- Chat rendering behavior in `frontend/src/components/chat/MessageBubble.tsx` only if needed for clearer toggle copy or hidden-count behavior.
- Focused tests in `frontend/tests/artifactCard.test.mjs`.
- Optional CSS polish in `frontend/src/index.css` only if the existing toggle needs clearer collapsed/expanded affordance.
- Plan/checklist updates and a final `DEVLOG.md` entry during the implementation pass.

## Contract Notes

- No `packages/shared/types.ts` change is required.
- No `docs/API_SPEC.md` change is required because artifact payload shape stays unchanged.
- Existing `Artifact.type`, `Artifact.previewUrl`, `Artifact.files[].name`, and `Artifact.files[].language` are enough to classify priority.
- Existing preview behavior remains right-panel based; this plan only changes chat list visibility and ordering.

## Proposed Ordering

1. Previewable HTML/web outputs:
   - `artifact.type === "webpage"`
   - artifacts with `previewUrl`
   - artifacts containing `.html` / `.htm` or `language === "html"`
2. README and Markdown documents:
   - file names matching `README.md`, `README.markdown`, etc.
   - other Markdown artifacts (`.md`, `.markdown`, `language === "markdown"`)
3. Other user-facing documents or files:
   - `document` / `file` artifacts that are not previewable HTML/Markdown
4. Source code artifacts:
   - `code` artifacts without previewable files
5. Change/diff artifacts:
   - `diff` artifacts remain after created outputs so the default collapsed view favors preview/open targets

Within each group, keep the original arrival order for stability. If two artifacts have the same priority, do not alphabetically reshuffle them.

## Implementation Steps

1. Add failing tests for the requested behavior:
   - default visible artifact count is three;
   - collapsed list shows the top three after sorting;
   - expanded list shows all artifacts in sorted order;
   - HTML/webpage and README/Markdown artifacts sort ahead of ordinary source files;
   - diff artifacts remain below output artifacts.
2. Update `MESSAGE_ARTIFACT_COLLAPSE_LIMIT` from `5` to `3`.
3. Replace the coarse `artifactMessageOrder()` with a preview-priority classifier that uses `isHtmlFile()` and `isMarkdownFile()`.
4. Preserve stable ordering by including original index as a tie-breaker in `getOrderedMessageArtifacts()`.
5. Review `MessageBubble` toggle copy:
   - current `展开剩余 N 个产物` is acceptable;
   - use `visibleArtifacts.hiddenCount` rather than recomputing from the constant if this makes the component less fragile.
6. Run verification and update checklist/DEVLOG.

## Tests

- `cd frontend && npm test`
- `cd frontend && npm run build`

## Out of Scope

- Backend artifact generation, persistence, or WebSocket payload changes.
- New artifact types or shared type changes.
- Grouping artifacts into folders or virtual bundles.
- Deduplicating generated files beyond the existing message/store merge by artifact id.
- P2 features such as applying diffs, artifact search, or full file-tree navigation in chat.

## Stability Assessment

Both requested behaviors are stable to implement because they are deterministic frontend presentation rules over data the app already receives. The main risk is classification ambiguity when an artifact contains multiple files; the plan resolves this by treating an artifact as high priority if any contained file is previewable, while card title/details continue to use existing presentation logic.
