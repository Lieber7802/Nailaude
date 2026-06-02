# M3 OpenCode Raw Code Reply Fix Plan

## Goal

Prevent OpenCode group-chat reply text from rendering raw source code in the message bubble while keeping generated files visible through artifact cards.

## Scope

- Harden OpenCode assistant text extraction when the CLI returns fenced code blocks or code-like text as a normal message part.
- Preserve concise human-readable summaries in `text_delta`.
- Keep file contents flowing through existing `file_created` / `file_modified` artifact events.

## Contract Notes

- No shared type, REST, or WebSocket schema changes.
- `text_delta` remains plain chat text.
- Artifact cards remain the canonical display for generated code and previews.

## Implementation Steps

- Add a regression test that reproduces a TSX code fence being streamed as assistant text after OpenCode writes a file.
- Sanitize assistant text before returning it from `_extract_text`.
- Fall back to the existing concise OpenCode execution summary when sanitized text has no prose left.
- Update checklist and DEVLOG after verification.

## Tests

- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q`
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py tests/test_m3_websocket_runtime.py tests/test_m4_artifact_preview.py -q`

## Out of Scope

- Frontend rendering changes.
- Changing OpenCode prompt contracts beyond reply text sanitization.
- Adding new dependencies.
