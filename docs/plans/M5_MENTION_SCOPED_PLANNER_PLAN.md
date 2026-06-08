# M5 Mention Scoped Planner Plan

## Goal

Prevent LLM planner tasks from targeting conversation participants that were not selected for the current dispatch run.

## Scope

- Backend WebSocket orchestration planning context.
- Focused regression coverage for explicit mention subsets.
- No frontend, adapter, shared type, or API payload changes.

## Contract Notes

- `mentions` remains the client-provided explicit agent list for the message.
- `PlannerContext.participants` remains a list of agents available for ready tasks, but will be scoped to the current dispatch set.
- `availableAgentCatalog` remains the full catalog for `capability_gap` recommendations.

## Implementation Steps

1. Add a regression test where a conversation has more participants than the current dispatch agent list.
2. Scope `plan_job()` planner participants to `job["agents"]`.
3. Keep no-mention behavior unchanged because `resolve_dispatch_agents()` already expands no-mention runs to all conversation participants.

## Tests

- `cd backend && .venv/bin/python -m pytest tests/test_m3_websocket_interactions.py -k "planner_context_is_scoped or non_mock_job_uses_deepseek_planner_wrapper"`

## Out of Scope

- Changing mention extraction in the frontend.
- Changing `availableAgentCatalog` recommendation semantics.
- Changing adapter fallback or runtime scheduling behavior.
