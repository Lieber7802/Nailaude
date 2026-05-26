# M2_4 Message Stream Plan

## Goal

Improve chat stream readability and runtime feedback.

## Scope

- Message avatar, role label, timestamp, and streaming indicator.
- Runtime banner for Orchestrator status, task status, thinking Agents, and errors.
- Preserve CodeCard rendering.

## Contract Notes

- Consume existing `agent_thinking`, `orchestrator_status`, `error`, `artifact`, and `message_done` events.

## Implementation Steps

- Extend UI store with per-conversation runtime state.
- Update `useWebSocket` event handlers.
- Update ChatArea and MessageBubble rendering.

## Tests

- Frontend build.
- WebSocket backend tests verify emitted runtime events.

## Out of Scope

- Message actions such as regenerate/copy.
