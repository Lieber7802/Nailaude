# M3 Collaboration API Contract

This appendix is authoritative for the M3 Orchestrator collaboration surfaces.
It supersedes earlier illustrative Team Board and Project State examples in
`API_SPEC.md`.

## Shared-State Endpoints

### `GET /api/v1/conversations/{id}/team-board`

```json
{
  "success": true,
  "data": {
    "conversationId": "conversation-id",
    "version": 2,
    "teamMembers": [],
    "decisions": [],
    "codeStandards": [],
    "openQuestions": [],
    "progress": {
      "completedTaskIds": [],
      "activeTaskIds": [],
      "blockedTaskIds": [],
      "pendingTaskIds": [],
      "currentFocus": ""
    },
    "recentNotes": [],
    "updatedAt": "2026-05-31T10:00:00Z"
  },
  "error": null
}
```

### `GET /api/v1/conversations/{id}/project-state`

```json
{
  "success": true,
  "data": {
    "conversationId": "conversation-id",
    "version": 2,
    "workspace": {
      "name": "demo",
      "workDir": "D:/AgentHub/workspaces/demo",
      "scannedAt": "2026-05-31T10:00:00Z",
      "fingerprint": "sha256"
    },
    "techStack": [],
    "fileTree": {
      "totalFiles": 1,
      "paths": ["README.md"],
      "truncated": false
    },
    "git": {
      "isRepository": false,
      "dirty": false,
      "recentCommits": []
    },
    "progressSummary": "",
    "recentChanges": [],
    "warnings": [],
    "updatedAt": "2026-05-31T10:00:00Z"
  },
  "error": null
}
```

## WebSocket Collaboration Events

The server emits full, monotonic `orchestrator_status` snapshots. Clients apply
only newer snapshots for the same run before updating banners, cards, or
derived state. Reconnects restore the latest persisted snapshot.

Additional server events:

- `orchestrator_input_required`
- `orchestrator_approval_required`
- `team_board_updated`
- `project_state_updated`

Additional client events:

- `orchestrator_input_response`
- `orchestrator_approval_response`
- `stop_generation`

`orchestrator_input_response` resumes clarification or confirms a recommended
Agent. Multi-question clarification answers are submitted atomically. The
server validates both `conversationId` and `runId` ownership before consuming a
paused job. `orchestrator_approval_response` resumes or cancels elevated write
work under the same ownership rule.

## Stabilized Runtime Semantics

- A Planner `cannot_plan` result becomes a failed orchestrator snapshot plus a
  recoverable WebSocket error. It is not emitted as an input card.
- A `write` task completes only when its per-task workspace audit records an
  actual filesystem change. Text-only fallback output is failed with a visible
  warning.
- Adapter downgrade, fallback execution, snapshot truncation, and audit
  warnings remain visible in orchestrator snapshots.
- Team Board and Project State are refreshed at each scheduler batch barrier so
  downstream handoffs receive current shared state.
- Persisted non-terminal runs cannot be resumed after process restart because
  their runtime queues are memory-only. On reconnect, the server reconciles
  them to `failed` with an explicit restart warning.
- The frontend reconnects with bounded exponential backoff and cancels pending
  reconnect timers when the conversation changes or the user disconnects.
