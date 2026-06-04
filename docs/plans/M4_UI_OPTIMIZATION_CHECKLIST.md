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
- [x] GFM Markdown rendering tests added
- [x] Artifact ordering and preview tab split tests added
- [x] Backend cancellation tests cover active and pre-execution run cancellation
- [x] Collaboration status and orchestrator UI tests added
- [x] Project/team summary failure degradation tests updated
- [x] Preview zoom range tests added

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
- [x] Right-side Markdown preview supports GFM rendering with heading anchors, blockquotes, tasks, tables, and inline syntax
- [x] Right-side Outputs tab excludes diff artifacts
- [x] Right-side Changes tab lists changed files and keeps details collapsed by default
- [x] Chat artifact cards order newly created files before changed files
- [x] Chat artifact cards hide status labels and remove copy/new-tab actions
- [x] User-facing "代理" labels replaced with "智能体"
- [x] Stop-generation cancels queued/pre-execution runs as well as active execution
- [x] Collaboration status only shows intelligent agents involved in the current run
- [x] Main intelligent-agent status card uses Chinese labels and checklist task rows
- [x] DeepSeek summary failures no longer appear as user-facing orchestrator warnings
- [x] HTML preview fills available fullscreen preview height
- [x] HTML preview supports free internal scaling from 25% to 300%

## Verification
- [x] Frontend tests pass
- [x] Frontend build passes
- [x] Browser smoke check completed
- [x] DEVLOG updated
