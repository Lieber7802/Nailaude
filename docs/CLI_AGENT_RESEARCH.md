# CLI Agent Research

## OpenCode

- Local command is available.
- `opencode run [message..] --format json --dir <workspace>` provides a one-shot integration path.
- `--session`, `--continue`, and `--fork` expose optional session reuse.
- `ProcessPool` terminates the process on timeout or cancellation.

## Codex

- A `codex.exe` entry is discoverable from the Codex desktop app install directory.
- On this machine, invoking `codex --help` returns an operating-system access-denied error.
- The adapter supports a standard one-shot `codex exec --full-auto <prompt>` path when a usable CLI is installed.
- The desktop-app executable is not considered a usable CLI; runtime falls back to `llm`, then permanent `mock`.

## Demo Fallback

CLI availability is optional. CI and the stable demo path use deterministic fake adapters or `MockAdapter`.

## M3 Verification Record

- DeepSeek: fake-transport JSON, streaming, timeout/retry, usage, planner, and summarizer coverage passed. A real API health call was intentionally skipped; no API key was written to `.env`.
- OpenCode: `opencode --help` and `opencode run --help` succeeded locally. The supported one-shot adapter command is recorded above.
- Codex: local discovery resolved to the desktop application path, but `codex --help` returned access denied. The adapter therefore treats this installation as unavailable and falls back to `llm`, then `mock`.
- Mock-first browser smoke: group chat produced two Agent responses and artifact cards.
