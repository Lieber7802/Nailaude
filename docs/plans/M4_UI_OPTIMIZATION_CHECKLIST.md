# M4 UI Optimization Checklist

## Docs
- [x] Plan created
- [x] Checklist created
- [x] `AGENTS.md`, `API_SPEC.md`, `types.ts`, `TASK_BREAKDOWN.md`, and M4 plans reviewed

## Tests
- [x] Artifact card presentation tests added
- [x] Chat Markdown parsing tests added
- [x] Markdown code-block regression tests added
- [x] Timestamp normalization tests added
- [x] Attachment summary tests added

## Implementation
- [x] Inline artifact previews removed from chat cards
- [x] Stop-generation button added to chat input
- [x] Left and right panes support resizing
- [x] Left and right panes support collapse/restore
- [x] Shared context panel hidden from chat stream
- [x] Agent reply Markdown rendered in messages
- [x] Collapse buttons moved to the divider-control area
- [x] Chat code-block Markdown renders for fenced and indented blocks
- [x] Chat timestamps match local current time
- [x] `@代理` button opens the mention selector
- [x] `附件` button opens file picker and carries selected-file context into the message

## Verification
- [x] Frontend tests pass
- [x] Frontend build passes
- [x] Browser smoke check completed
- [x] DEVLOG updated
