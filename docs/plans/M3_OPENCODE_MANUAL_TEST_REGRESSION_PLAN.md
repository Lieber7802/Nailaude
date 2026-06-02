# M3 OpenCode Manual Test Regression Plan

## Goal

Fix the manual-test regressions found on 2026-06-02:

- OpenCode protocol/code-like text can overflow the chat bubble.
- Orchestrator still shows `Workspace missing`.
- Artifact preview can show `Preview file not found`.

## Scope

- Backend planner normalization, conversation workspace creation, OpenCode output filtering.
- Frontend chat wrapping and preview fallback behavior.
- No API/shared type contract changes.

## Contract Notes

- Preview route remains `/preview/{conversation_id}/{file_path}`.
- Artifact events continue to carry `files[]` content and optional `previewUrl`.
- `Conversation.workDir` remains unchanged in API responses.

## Implementation Steps

1. Add tests for planner write access normalization when the model incorrectly returns read access for implementation tasks.
2. Add tests ensuring relative workspaces are created when conversations are created.
3. Add OpenCode adapter tests for malformed protocol fragments.
4. Make preview use artifact HTML content before remote preview URL to avoid 404 when the file is not on disk.
5. Add CSS wrapping for abnormal long text in chat bubbles.

## Tests

- `tests/test_m3_planner.py`
- `tests/test_m1_1_api.py`
- `tests/test_m3_cli_adapters.py`
- Frontend build as smoke verification.

## Out of Scope

- Rendering server-side Flask/Jinja apps inside the preview iframe.
- Changing model/provider configuration or `.env` secrets.
