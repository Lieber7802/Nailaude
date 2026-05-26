# M2_6 Builtin Agent Data Plan

## Goal

Keep M2 demo Agents predictable and Mock-backed.

## Scope

- Preserve code, review, and docs builtin Agents.
- Keep all builtin Agents on `mock`.
- Avoid showing `platformId` in ordinary user UI.

## Contract Notes

- No shared type changes.
- No platform configuration changes.

## Implementation Steps

- Reuse existing seed data.
- Render public Agent fields only in chat UI.

## Tests

- Existing agent seed tests.
- Frontend build confirms type usage.

## Out of Scope

- Agent CRUD UI and real platform binding.
