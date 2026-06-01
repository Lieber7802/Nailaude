# CLI Agent Research

## OpenCode

- Local command is available.
- `opencode run [message..] --format json --dir <workspace>` provides a one-shot integration path.
- `--session`, `--continue`, and `--fork` expose optional session reuse.
- `ProcessPool` terminates the process on timeout or cancellation.

## Codex

- Local command is available at `/opt/homebrew/bin/codex`.
- `codex --help` and `codex exec --help` succeed from the terminal.
- The current non-interactive integration path is:
  `codex --ask-for-approval never exec --json --cd <workspace> --sandbox workspace-write --skip-git-repo-check <prompt>`.
- `--json` emits JSONL events. Agent text is available in `item.completed` events whose item type is `agent_message`.
- The adapter snapshots the workspace before and after execution and converts created/modified text files into standard AgentHub file events.
- Runtime still falls back to `llm`, then permanent `mock`, if Codex is unavailable or fails for read-only work.

## Demo Fallback

CLI availability is optional. CI and the stable demo path use deterministic fake adapters or `MockAdapter`.

## M3 Verification Record

- DeepSeek: fake-transport JSON, streaming, timeout/retry, usage, planner, and summarizer coverage passed. A real API health call was intentionally skipped; no API key was written to `.env`.
- OpenCode: `opencode --help` and `opencode run --help` succeeded locally. The supported one-shot adapter command is recorded above.
- Codex: real local adapter smoke succeeded. `CodexAdapter.run_task()` created `adapter_smoke.txt`, emitted a `text_delta`, emitted `file_created`, and finished with `done`.
- Mock-first browser smoke: group chat produced two Agent responses and artifact cards.
