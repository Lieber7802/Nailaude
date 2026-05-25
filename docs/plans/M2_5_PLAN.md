# M2_5 Orchestrator Foundation Plan

## Goal

Add rule-based Orchestrator dispatch for M2 group chat demos.

## Scope

- Build sequential DispatchPlan from mentions or conversation participants.
- Push Orchestrator status over WebSocket.
- Execute each task through MockAdapter.

## Contract Notes

- Reuse `DispatchPlan`, `Task`, and `WSOrchestratorStatus`.
- Adapter context stays minimal in M2.

## Implementation Steps

- Implement `OrchestratorService.build_dispatch_plan()`.
- Update WebSocket handler to call Orchestrator and stream each task.
- Persist one Agent message per task.

## Tests

- Unit-style Orchestrator plan test.
- Multi-Agent WebSocket integration test.

## Out of Scope

- LLM intent parsing and parallel execution.
