# Codex CLI Testing and Cross-Platform Guide

## Purpose

This guide records the issues found while integrating and testing the Nailaude
Codex CLI adapter. It also defines the Windows and macOS development
expectations for the team.

Nailaude runs Codex as an independent one-shot subprocess. It does not reuse or
modify the Codex Desktop session used for project development.

## Final Runtime Strategy

The adapter command is:

```text
codex --ask-for-approval never exec --ephemeral --json \
  --cd <workspace> --sandbox <mode> --skip-git-repo-check <prompt>
```

Platform behavior:

| Platform | Binary resolution | Sandbox mode |
|---|---|---|
| Windows | Prefer `%LOCALAPPDATA%\OpenAI\Codex\bin\*\codex.exe`, then fall back to PATH | `danger-full-access` |
| macOS / Linux | Use `CODEX_BINARY_PATH` or PATH | `workspace-write` |

Each Nailaude task creates:

- A temporary `CODEX_HOME`.
- A temporary Codex provider config.
- A loopback-only Responses-to-Chat bridge.
- A random per-run bridge token.

The DeepSeek API key stays in the backend process. The spawned CLI receives only
the short-lived loopback bridge token.

## Issues Found During Real Testing

### 1. Windows PATH can point to an unusable Codex binary

Symptom:

```text
Access is denied
```

Cause:

Codex Desktop exposes a Microsoft Store package resource binary on PATH:

```text
C:\Program Files\WindowsApps\...\app\resources\codex.exe
```

That file has an application-identity ACL. A normal FastAPI subprocess cannot
start it.

Resolution:

On Windows, Nailaude first discovers the runnable Codex Desktop cache under:

```text
%LOCALAPPDATA%\OpenAI\Codex\bin\*\codex.exe
```

Do not hard-code a Windows cache hash. It changes when Codex Desktop updates.

### 2. Current Codex custom providers require Responses wire format

Symptom:

```text
wire_api = "chat" is no longer supported. set wire_api = "responses"
```

Cause:

Current Codex CLI custom providers use the Responses API wire format. DeepSeek
documents an OpenAI-compatible Chat Completions endpoint.

Resolution:

Nailaude starts a backend-only loopback bridge per task:

```text
Codex Responses request -> local bridge -> DeepSeek Chat Completions
DeepSeek SSE response    -> local bridge -> Codex Responses SSE
```

The bridge translates text deltas, tool definitions, function calls, and tool
results.

### 3. Reusing the developer Codex configuration is the wrong boundary

Risk:

A subprocess that reads the active `~/.codex` directory can inherit developer
providers, thread state, plugin state, or credentials. It can also accidentally
mutate the desktop session configuration.

Resolution:

Every task uses a new temporary `CODEX_HOME`. Nailaude also removes desktop-only
environment variables such as `CODEX_THREAD_ID` before spawning the CLI.

### 4. Windows Codex sandbox initialization fails on this host

Symptoms:

```text
windows sandbox: spawn setup refresh
```

and, when trying the `unelevated` workaround:

```text
Access to the path ... is denied
```

Cause:

The Windows sandbox helper cannot initialize correctly on the tested machine.
The `unelevated` mode starts, but it cannot write the task workspace.

Resolution:

Nailaude intentionally runs Codex directly on the Windows host:

```text
--sandbox danger-full-access
```

macOS and Linux continue to use:

```text
--sandbox workspace-write
```

### 5. A finished CLI can still appear to hang on Windows

Symptom:

The main `codex.exe` process exits with return code `0`, but `communicate()` does
not return and the adapter eventually reports a false timeout.

Cause:

A long-lived Windows PowerShell helper used by Codex command parsing inherits
stdout or stderr handles. Waiting for pipe EOF is therefore not equivalent to
waiting for the main CLI process to exit.

Resolution:

`ProcessPool` treats the main process return code as authoritative, drains pipes
for a bounded interval, and then closes inherited pipe transports.

### 6. Temporary directories can remain locked briefly

Symptom:

Immediately deleting a smoke-test workspace can fail with:

```text
The process cannot access the file because it is being used by another process
```

Resolution:

For disposable smoke directories, retry cleanup after a short delay. Do not
interpret a short-lived cleanup lock as a failed Agent task if the CLI returned
success and the expected artifact exists.

An earlier failed Windows sandbox probe may also leave a protected
`.sandbox-secrets\sandbox_users.json`. Its ACL can prevent normal cleanup.

### 7. Configure `.env`, not `.env.example`

The backend reads:

```text
backend/.env
```

The tracked template must remain:

```text
DEEPSEEK_API_KEY=your_deepseek_api_key
```

Never write a real key into `backend/.env.example`, documentation, test output,
or Git history.

## Verification Ladder

Run tests in this order so failures stay diagnosable.

### 1. Focused deterministic suite

```bash
cd backend
python -m pytest \
  tests/test_m3_process_pool.py \
  tests/test_m3_deepseek_responses_bridge.py \
  tests/test_m3_cli_adapters.py \
  tests/test_m3_codex_cli_smoke.py -q
```

Expected result at the time this guide was written:

```text
18 passed
```

### 2. Health check

Confirm that:

- The resolved CLI binary is executable.
- `DEEPSEEK_API_KEY` is available to the backend.
- `CodexAdapter.health_check()` returns `True`.

### 3. Live text smoke

Ask Codex to reply exactly:

```text
LIVE_CODEX_DEEPSEEK_OK
```

Expected Agent events:

```text
text_delta -> done
```

### 4. Live file smoke

Ask Codex to create:

```text
live_codex_deepseek_smoke.txt
```

with exact content:

```text
LIVE_FILE_OK
```

Expected Agent events:

```text
text_delta -> file_created -> done
```

### 5. Full backend regression

```bash
cd backend
python -m pytest -q
```

Expected result at the time this guide was written:

```text
137 passed
```

## Windows and macOS Collaboration

Using Windows and macOS together is workable. The application code is mostly
portable because it uses `pathlib.Path`, normalized artifact paths, and
argument-array subprocess execution. Team members should still expect
environment-specific behavior at the CLI boundary.

### Known differences

| Area | Windows | macOS | Team rule |
|---|---|---|---|
| Codex binary | Desktop cache under `%LOCALAPPDATA%` may be required | Common locations include `/opt/homebrew/bin/codex` and `/usr/local/bin/codex` | Prefer `CODEX_BINARY_PATH=codex`; set an explicit local path only when PATH discovery fails |
| Codex execution mode | Direct host execution with `danger-full-access` | `workspace-write` | Run the live file smoke on both operating systems |
| Shell tools generated by an Agent | Usually PowerShell semantics | Usually POSIX shell semantics | Avoid shell-specific prompts; use Python or repo scripts for shared automation |
| Path separator | `\` | `/` | Use `pathlib.Path` in Python and normalize stored artifact paths to `/` |
| Absolute workspace path | Drive-letter path such as `D:\Nailaude\workspaces\demo` | POSIX path such as `/Users/name/Nailaude/workspaces/demo` | Never commit local absolute paths |
| Line endings | Git may check out CRLF when `core.autocrlf=true` | Usually LF | Avoid formatting-only commits; review `git diff --check` before handoff |
| File-name casing | Usually case-insensitive | Usually case-insensitive by default, but can vary | Match import and file-name casing exactly; avoid case-only renames |
| Temporary file locks | More common after subprocess exit | Less common | Retry disposable cleanup briefly |
| Executable suffix | `.exe` | No suffix | Keep platform-specific lookup inside adapters |

### Current repository observations

- The Codex adapter has an explicit Windows resolver and platform-specific
  execution mode.
- Workspace and preview services use `pathlib.Path`.
- Artifact paths are normalized from `\` to `/` before storage or preview.
- Conversation workspace validation accepts Windows drive-letter paths and
  validates normal POSIX paths under the project `workspaces` directory.
- A persisted or copied absolute `workDir` is machine-specific. A Windows value
  such as `D:\Nailaude\workspaces\demo` is not a usable macOS workspace, and a
  macOS `/Users/...` value is not a usable Windows workspace. Prefer repository
  relative values such as `workspaces/demo` in shared examples, API fixtures,
  and manual test instructions.
- `ProcessPool` uses `asyncio.create_subprocess_exec()` with an argument list,
  not shell command-string interpolation.
- The repository currently has no `.gitattributes`. A Windows checkout with
  `core.autocrlf=true` can produce LF/CRLF warnings. Consider adding an explicit
  line-ending policy in a dedicated cleanup change if churn becomes noisy.

### Minimum team verification matrix

Before merging CLI adapter changes:

| Check | Windows developer | macOS developer |
|---|---|---|
| `CodexAdapter.health_check()` | Required | Required |
| Live text smoke | Required | Required |
| Live file smoke | Required | Required |
| Focused Codex suite | Required | Required |
| Full backend regression | Required before merge | Required before merge |
| `git diff --check` | Required | Required |

## Troubleshooting Checklist

1. Confirm the real key is in `backend/.env`, not `.env.example`.
2. Print the resolved Codex binary path without printing credentials.
3. Run `codex --help` against that exact binary.
4. Confirm the generated provider config uses `wire_api = "responses"`.
5. Confirm `CODEX_HOME` is temporary and different from the developer home.
6. On Windows, confirm the command contains `--sandbox danger-full-access`.
7. Run the deterministic fake-upstream smoke before spending time on live API
   calls.
8. If a successful CLI appears to time out, inspect inherited stdout and stderr
   handles before changing API retry behavior.
9. If only workspace cleanup fails, retry after a short delay and inspect ACLs
   before recursively deleting protected temporary directories.
