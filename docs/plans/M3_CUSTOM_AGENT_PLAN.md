# M3 Custom Agent Plan

## Goal

Allow users to create custom Agent roles from the workspace UI and immediately see them in the left sidebar agent list.

## Scope

- Reuse existing backend `/agents` and `/platforms` APIs.
- Add frontend create-agent API helpers and a modal form.
- Wire the left sidebar agent action and chat top-bar add-agent action to the same create flow.
- Add focused backend regression coverage for custom agent creation.
- Update API docs, checklist, and DEVLOG.

## Contract Notes

- `CreateAgentDTO` already exists in `packages/shared/types.ts`.
- `POST /api/v1/agents` accepts camelCase `systemInstruction` and `platformId`.
- `GET /api/v1/platforms` provides platform options.
- No shared type changes are expected.

## Implementation Steps

1. Add backend regression test for custom agent creation and list visibility.
2. Add frontend API helpers for creating agents and listing platforms.
3. Add `AgentCreateModal` with name, avatar, role/function description, capabilities, system instruction, and platform selection.
4. Wire `Workspace` creation state to left sidebar and chat top bar.
5. Update styles so the controls fit the existing sidebar and header density.
6. Run targeted backend test, frontend tests, build, and lint.

## Tests

```bash
cd backend
../.venv/bin/python -m pytest tests/test_m1_1_api.py::test_create_custom_agent_persists_and_lists

cd ../frontend
npm test
npm run build
npm run lint
```

## Out of Scope

- Editing or deleting custom agents from the workspace sidebar.
- Adding a newly created agent to an existing conversation automatically.
- New platform configuration flows.
