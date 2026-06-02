# M3 OpenCode Review Output Fix Plan

## Goal

Fix reviewer-agent turns where OpenCode performs a read-only review but returns only protocol/tool events, causing AgentHub to display a generic execution summary such as `未检测到工作区文件变更。`

## Scope

- OpenCode adapter prompt and fallback behavior for read-only review tasks.
- Keep review tasks read-only; no workspace write access change.
- No frontend/API/shared type changes.

## Contract Notes

- Review output remains a normal `text_delta` message.
- Artifact events are unchanged.
- `accessMode=read` remains correct for review tasks.

## Implementation Steps

1. Add a regression test for a read-only review task that receives only OpenCode protocol/tool events.
2. Add a review-specific prompt contract: do not modify files and return a final actionable review.
3. Replace generic fallback summaries with a local, conservative review summary when the task is read-only review and OpenCode returns no final text.
4. Verify adapter tests and update DEVLOG.

## Tests

- `tests/test_m3_cli_adapters.py` should assert review fallback contains actionable review text and does not say only that no workspace changes were detected.

## Out of Scope

- Full static-analysis engine.
- Changing agent roles or platform bindings.
