# M2_3 Mention Interaction Plan

## Goal

Allow users to @ mention Agents while composing messages.

## Scope

- Floating MentionSelector when the cursor is after `@`.
- Filter by Agent name or capabilities.
- Insert `@AgentName ` into the textarea.
- Send parsed mentions with the WebSocket payload.

## Contract Notes

- Reuse existing `Mention` and `SendMessageDTO`.
- Single chat without explicit @ defaults to the only participant.

## Implementation Steps

- Implement MentionSelector.
- Update MessageInput cursor tracking and mention insertion.
- Add `extractMentions()` helper in the API service wrapper.

## Tests

- Frontend build.
- Manual demo: type `@`, select an Agent, send message.

## Out of Scope

- Keyboard navigation and rich-text tokens.
