---
name: nailaude-module-development
description: Use when implementing Nailaude modules, M-series milestone tasks, backend/frontend features, agent adapters, artifact flows, WebSocket work, or checklist-driven project changes in the Nailaude repository.
---

# Nailaude Module Development

## Overview

Use this project skill to keep Nailaude development modular, contract-first, Mock-first, and verifiable. It coordinates project-specific rules with the usual plan, TDD, execution, and verification workflows.

## Required Workflow

1. **Ground in project contracts**
   - Read `AGENTS.md`.
   - Read `docs/API_SPEC.md` and `packages/shared/types.ts` before API, WebSocket, shared type, frontend service, or adapter work.
   - Read `docs/TASK_BREAKDOWN.md` and relevant `docs/plans/*` files for milestone scope.

2. **Define the module boundary**
   - State the milestone/task id, target files, expected behavior, and out-of-scope items.
   - Keep changes inside the relevant module boundary from `AGENTS.md`.
   - Do not implement P2 scope unless explicitly requested.

3. **Create or update planning artifacts**
   - Save module plans in `docs/plans/` as `<MODULE>_PLAN.md`.
   - Save execution checklists in `docs/plans/` as `<MODULE>_CHECKLIST.md`.
   - Make checklist items verifiable, not vague.

4. **Implement with tests first**
   - Write failing tests before production code for features, bug fixes, and behavior changes.
   - Keep REST/WS contracts aligned with `API_SPEC.md` and `packages/shared/types.ts`.
   - If `packages/shared/types.ts` changes, update `docs/API_SPEC.md` in the same task.

5. **Respect Nailaude constraints**
   - Preserve `MockAdapter`; it is a permanent fallback.
   - For new Agent behavior, make Mock cover the scenario before real LLM/CLI integration.
   - Keep `backend/adapters/` business-agnostic.
   - Do not expose `platformId` in ordinary user-facing UI.
   - Do not edit `.env` secrets.

6. **Verify and record**
   - Run the narrowest relevant test command, then a broader verification when practical.
   - Update the checklist with actual completed items.
   - Append a concise entry to `DEVLOG.md` with changed files, interface changes, tests, next steps, and teammate notes.
   - Final response must include verification evidence and remaining risks.

## Planning Template

```markdown
# <MODULE> Plan

## Goal

## Scope

## Contract Notes

## Implementation Steps

## Tests

## Out of Scope
```

## Checklist Template

```markdown
# <MODULE> Checklist

## Docs
- [ ] Plan created or updated
- [ ] Checklist created or updated

## Implementation
- [ ] Contract reviewed
- [ ] Tests written first
- [ ] Feature implemented

## Verification
- [ ] Targeted tests pass
- [ ] Broader smoke check completed
- [ ] DEVLOG updated
```

## Stop Conditions

Stop and ask before continuing if:
- The requested change conflicts with `API_SPEC.md` or `packages/shared/types.ts`.
- A dependency must be added and the reason is not already in the plan.
- The task requires deleting or bypassing MockAdapter.
- Existing user changes make the module boundary unclear.
