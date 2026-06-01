# M3 Codex DeepSeek Isolation Checklist

## Docs

- [x] Plan created.
- [x] Checklist created.
- [x] Existing adapter and API contracts reviewed.

## Root Cause

- [x] Reproduced Microsoft Store package ACL failure.
- [x] Located runnable Codex CLI cache outside the protected package.
- [x] Confirmed Codex custom providers require Responses wire API.
- [x] Confirmed DeepSeek documents Chat Completions compatibility.

## Implementation

- [x] Tests written first and verified failing.
- [x] ProcessPool subprocess environment injection implemented.
- [x] Loopback Responses-to-Chat bridge implemented.
- [x] Codex adapter isolated CLI environment implemented.
- [x] Windows runnable CLI resolution implemented.
- [x] Windows sandbox helper bypassed with documented direct host execution.

## Verification

- [x] Targeted tests pass.
- [x] Real Codex CLI fake-upstream smoke passes.
- [x] Live Codex CLI DeepSeek smoke passes.
- [x] Full backend regression passes.
- [x] DEVLOG updated.

## Final Evidence

- Focused Codex isolation suite -> `18 passed`.
- Full backend regression -> `137 passed`.
- Live text smoke -> `LIVE_CODEX_DEEPSEEK_OK`.
- Live file smoke -> created `live_codex_deepseek_smoke.txt` with
  `LIVE_FILE_OK\n`, then emitted `text_delta`, `file_created`, and `done`.
