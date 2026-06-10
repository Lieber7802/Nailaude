# PROJECT_RENAME Plan

## Goal

Rename the completed project to the official name nailaude and replace the minimal README with a complete project README.

## Scope

- Update tracked source, tests, configuration, and documentation references to use nailaude.
- Update runtime-facing names such as API title, health service name, mock preview title, default SQLite filename, temporary directories, and Codex bridge environment variable names.
- Rewrite the root `README.md` with project overview, architecture, features, setup, development, verification, and repository layout.
- Update the project workflow plan/checklist and append a DEVLOG entry.

## Contract Notes

- `docs/API_SPEC.md` and `packages/shared/types.ts` were reviewed before edits.
- No API payload shapes or shared type structures are changed.
- The only contract-adjacent changes are product naming strings and default local configuration names.

## Implementation Steps

1. Add this plan and a checklist for the rename task.
2. Apply a case-aware repository rename to nailaude/Nailaude/NAILAUDE where appropriate.
3. Rewrite `README.md` as the authoritative public project introduction.
4. Update tests that assert product strings or environment variable names.
5. Run targeted source scans and available frontend/backend verification.
6. Append a DEVLOG entry.

## Tests

- `rg` checks for stale previous product-name references in tracked project files.
- Backend targeted tests covering renamed runtime strings and env vars.
- Frontend test/build smoke if dependencies are available.

## Out of Scope

- Renaming the current local workspace directory.
- Changing API schemas, database schemas, or feature behavior.
- Rebranding external third-party names such as Codex, OpenCode, DeepSeek, React, Vite, or FastAPI.
