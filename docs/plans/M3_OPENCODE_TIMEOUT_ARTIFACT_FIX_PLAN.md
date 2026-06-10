# M3 OpenCode Timeout Artifact Fix Plan

## Goal

When OpenCode times out after already writing workspace files, surface those file changes as Nailaude artifacts instead of leaving the chat with an empty failed agent message.

## Scope

- OpenCode adapter timeout/error handling.
- Preserve existing raw-output cleanup and file-event behavior.
- Explain local timeout configuration for manual testing.

## Contract Notes

- No REST, WebSocket, or shared TypeScript contract changes.
- Artifact events continue to use existing `file_created` / `file_modified` adapter events.
- Failed CLI execution can still report an error; partial artifacts should still be visible.

## Implementation Steps

1. Add a regression test where the process pool writes `index.html` and then raises `ProcessPoolError("process timed out")`.
2. Update OpenCode adapter to snapshot the workspace after `ProcessPoolError`.
3. If file changes exist, emit a concise text summary and file events before the error event.
4. Verify targeted adapter tests.

## Tests

- `tests/test_m3_cli_adapters.py` should assert timeout-written files produce file events and no raw code text.

## Out of Scope

- Frontend rendering changes.
- Changing user `.env` secrets.
- Retrying or resuming timed-out OpenCode sessions.
