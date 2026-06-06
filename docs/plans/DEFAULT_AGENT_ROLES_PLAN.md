# Default Agent Roles Plan

## Goal

Add a built-in product architect agent, enrich the default built-in agent role prompts, and make planner/adapter behavior route requirements, PRD, SPEC, and checklist work to product architecture while keeping README work on the documentation agent.

## Scope

- `backend/app/services/seed.py`
- `backend/app/services/planner_prompt.py`
- `backend/app/services/orchestrator_planner.py`
- `backend/app/adapters/opencode.py`
- Focused backend tests under `backend/tests/`
- `docs/plans/DEFAULT_AGENT_ROLES_CHECKLIST.md`
- `DEVLOG.md`

## Contract Notes

- No shared TypeScript type changes.
- No REST or WebSocket payload shape changes.
- Built-in agents continue to use existing Agent fields: `name`, `description`, `capabilities`, `systemInstruction`, `platformId`, and `isBuiltin`.
- Existing local databases should receive updated built-in prompts on the next seed pass.

## Implementation Steps

1. Add tests proving built-in seed data includes 产品架构师 and enriched prompts for all built-in agents.
2. Add tests proving existing built-in agents have prompts/descriptions/capabilities refreshed during seeding.
3. Add planner tests for product-architecture routing and README routing.
4. Add adapter tests proving document-planning tasks do not trigger the HTML preview contract while implementation tasks still do.
5. Update built-in agent seed data.
6. Update planner prompt and deterministic planner normalization/routing helpers.
7. Update OpenCode preview-contract gating for documentation/planning tasks.
8. Run focused backend tests, backend full tests, and frontend tests/build.

## Tests

```bash
cd backend
.venv/bin/python -m pytest tests/test_m1_1_api.py tests/test_m3_planner.py tests/test_m3_cli_adapters.py
.venv/bin/python -m pytest
cd ../frontend
npm test
npm run build
```

## Out of Scope

- Frontend layout or UI copy changes.
- New database migration.
- New dependencies.
