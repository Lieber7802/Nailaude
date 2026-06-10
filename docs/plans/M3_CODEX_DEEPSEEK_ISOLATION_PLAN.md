# M3 Codex DeepSeek Isolation Plan

## Goal

Run the Nailaude Codex adapter through an isolated Codex CLI instance backed by the DeepSeek API without reading, mutating, or reusing the active Codex Desktop configuration.

## Scope

- Add a backend-only Responses-to-Chat bridge for Codex CLI and DeepSeek.
- Extend `ProcessPool` with explicit subprocess environment injection.
- Update `CodexAdapter` to resolve a runnable Windows CLI cache, use an isolated temporary `CODEX_HOME`, and route the CLI through the local bridge.
- Add focused bridge, process pool, and adapter tests.
- Update local setup documentation and DEVLOG verification notes.

## Contract Notes

- Preserve `AgentAdapter.run_task(work_dir, instruction, context)`.
- Preserve existing AgentEvent types and MockAdapter fallback behavior.
- Keep `DEEPSEEK_API_KEY` backend-only and load it from runtime environment.
- Do not write to the active Codex Desktop home at `~/.codex`.
- Do not change shared TypeScript types or public WebSocket contracts.

## Root Cause

1. `CODEX_BINARY_PATH=codex` resolves to the Microsoft Store package resource binary on Windows.
2. That package resource has an application-identity ACL and cannot be started by the FastAPI backend process.
3. Runnable Codex CLI cache binaries exist under `%LOCALAPPDATA%\OpenAI\Codex\bin`.
4. Current Codex CLI releases require custom providers to use the Responses wire API.
5. DeepSeek documents an OpenAI-compatible Chat Completions endpoint, so Nailaude needs a backend-only local protocol bridge.

## Implementation Steps

1. Translate Codex Responses request input, tools, and tool results into DeepSeek Chat Completions payloads.
2. Translate DeepSeek SSE text and function-call deltas into Codex Responses SSE events.
3. Bind the bridge to loopback only with a per-run bearer token.
4. Generate a temporary Codex home and provider config for each Nailaude task.
5. Pass the isolated home and bridge token only to the spawned Codex subprocess.
6. Resolve a runnable Windows cached CLI before falling back to PATH.
7. Run the Windows CLI directly on the host with `danger-full-access` because
   the upstream `workspace-write` sandbox helper cannot initialize on this
   host. Keep `workspace-write` on non-Windows platforms.

## Tests

- Verify ProcessPool passes an explicit environment to child processes.
- Verify Responses input and tools become DeepSeek chat messages and tools.
- Verify text and function-call SSE events become valid Responses events.
- Verify Codex adapter uses a runnable cached Windows CLI and isolated environment.
- Verify ProcessPool returns after the main CLI exits even if a Windows helper
  inherits stdout or stderr handles.
- Run a real Codex CLI smoke against a deterministic fake DeepSeek upstream.
- Run a live DeepSeek smoke when `DEEPSEEK_API_KEY` is available in the backend runtime.

## Out of Scope

- Changing the active Codex Desktop configuration.
- Persisting API keys in repository files.
- Supporting every Responses API built-in tool type.
- Frontend changes.
