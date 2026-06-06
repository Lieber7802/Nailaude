# M5 Artifact List Prioritization Checklist

## Docs

- [x] Plan created for review
- [x] Checklist created for review
- [x] Contract reviewed in `docs/API_SPEC.md` and `packages/shared/types.ts`

## Research

- [x] Existing MessageBubble artifact merge/render path identified
- [x] Existing artifact card helper and tests identified
- [x] Confirmed no backend/API/shared-type change is required

## Implementation

- [x] Add RED tests for default three-card collapse
- [x] Add RED tests for HTML/webpage priority
- [x] Add RED tests for README/Markdown priority
- [x] Add RED tests for stable same-priority ordering
- [x] Change collapse limit from 5 to 3
- [x] Implement artifact preview-priority classifier
- [x] Keep diff artifacts below output artifacts
- [x] Simplify MessageBubble hidden-count usage if needed

## Verification

- [x] `cd frontend && npm test`
- [x] `cd frontend && npm run build`
- [ ] Manual chat smoke with more than three artifacts (not run in browser; covered by focused artifact list tests)
- [x] DEVLOG updated after implementation
