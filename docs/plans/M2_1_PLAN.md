# M2_1 Conversation List Plan

## Goal

Make the left conversation list usable for M2 demos.

## Scope

- Search by title or latest message.
- Show recent message preview, conversation type, and participants.
- Support stable select/delete interactions.

## Contract Notes

- Keep `GET /conversations?page&pageSize&search`.
- Return `lastMessage` using the existing optional `Conversation.lastMessage` field.

## Implementation Steps

- Add backend list query support for latest message preview and search.
- Update frontend API client to pass `search`.
- Replace static list rows with searchable, scrollable rows.

## Tests

- Backend test verifies search can match latest message and returns `lastMessage`.
- Frontend build verifies type integration.

## Out of Scope

- Pagination UI beyond the existing API paging parameters.
