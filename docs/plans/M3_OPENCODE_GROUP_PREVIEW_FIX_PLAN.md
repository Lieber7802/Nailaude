# M3 OpenCode Group Preview Fix Plan

## Goal

Keep frontend chat text concise for OpenCode group chats and ensure app/page preview requests produce a previewable HTML artifact instead of only documentation.

## Scope

- Harden OpenCode JSON output parsing so raw objects, tool payloads, and session metadata are not streamed as chat text.
- Add an OpenCode preview contract for write tasks that request pages, apps, mini programs, or preview.
- Retry once with a focused repair prompt when such a task creates no HTML preview entry.
- Verify artifact creation still emits webpage previews through the existing ArtifactService path.

## Contract Notes

- No shared type, REST, or WebSocket schema changes.
- Chat `text_delta` remains concise process/result text.
- Files and previewable app content continue to flow through artifact events.

## Tests

- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q`
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py tests/test_m3_websocket_runtime.py tests/test_m4_artifact_preview.py -q`
- `cd backend && ../.venv/bin/python -m pytest -q`

## Out of Scope

- Changing frontend rendering behavior.
- Real network smoke with DeepSeek/OpenCode credentials.
