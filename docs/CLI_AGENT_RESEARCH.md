# CLI Agent Research

For the full Codex troubleshooting record and the Windows/macOS collaboration
matrix, see `docs/CODEX_CLI_CROSS_PLATFORM_GUIDE.md`.

## OpenCode

- Local command is available.
- `opencode run [message..] --format json --dir <workspace>` provides a one-shot integration path.
- `--session`, `--continue`, and `--fork` expose optional session reuse.
- `ProcessPool` terminates the process on timeout or cancellation.

## Codex

- macOS local command is available at `/opt/homebrew/bin/codex`.
- Windows Codex Desktop exposes a protected Microsoft Store package resource on PATH. The backend cannot start that file because its ACL requires the app identity.
- Windows Codex Desktop also installs a runnable CLI cache under `%LOCALAPPDATA%\OpenAI\Codex\bin`. AgentHub resolves that cache before PATH.
- The current non-interactive integration path is:
  `codex --ask-for-approval never exec --ephemeral --json --cd <workspace> --sandbox <mode> --skip-git-repo-check <prompt>`.
  AgentHub intentionally uses `danger-full-access` on Windows, which runs the
  CLI directly on the host without the Codex filesystem sandbox. Other
  platforms continue to use `workspace-write`.
- `--json` emits JSONL events. Agent text is available in `item.completed` events whose item type is `agent_message`.
- The adapter snapshots the workspace before and after execution and converts created/modified text files into standard AgentHub file events.
- Current Codex CLI releases require custom providers to use the Responses wire API. DeepSeek documents Chat Completions compatibility, so AgentHub starts a loopback-only per-task Responses-to-Chat bridge.
- Each AgentHub task uses a temporary `CODEX_HOME` plus a per-run bridge token. It does not read or mutate the active Codex Desktop configuration.
- On this Windows host, Codex `workspace-write` fails during `windows sandbox: spawn setup refresh`, while the documented `unelevated` workaround cannot write the task workspace. AgentHub therefore intentionally runs Codex directly on the host with `danger-full-access` on Windows only. The adapter still sets the workspace root, snapshots only that workspace, and keeps the DeepSeek credential in the backend process.
- Runtime still falls back to `llm`, then permanent `mock`, if Codex is unavailable or fails for read-only work.

## Demo Fallback

CLI availability is optional. CI and the stable demo path use deterministic fake adapters or `MockAdapter`.

## M3 Verification Record

- DeepSeek: fake-transport JSON, streaming, timeout/retry, usage, planner, and summarizer coverage passed. A real API health call was intentionally skipped; no API key was written to `.env`.
- OpenCode: `opencode --help` and `opencode run --help` succeeded locally. The supported one-shot adapter command is recorded above.
- Codex: real local adapter smoke succeeded. `CodexAdapter.run_task()` created `adapter_smoke.txt`, emitted a `text_delta`, emitted `file_created`, and finished with `done`.
- Mock-first browser smoke: group chat produced two Agent responses and artifact cards.
