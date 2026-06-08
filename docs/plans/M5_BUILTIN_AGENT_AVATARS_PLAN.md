# M5 Builtin Agent Avatars Plan

## Goal

Replace the four builtin agent text avatars with the provided image avatars in this order: 代码工匠, 审查大师, 文档专家, 产品架构师.

## Scope

- Store the four provided PNG files as frontend public assets.
- Update builtin agent seed avatar values to image URLs.
- Update frontend avatar rendering so image URLs display as images wherever agent avatars appear.
- Keep custom text/emoji avatars supported.

## Contract Notes

- `docs/API_SPEC.md` and `packages/shared/types.ts` were reviewed.
- `Agent.avatar` already supports `emoji 或图片 URL`, so no shared type change is needed.
- The REST response shape stays unchanged; only builtin seed values change from letters to image paths.

## Implementation Steps

1. Add agent avatar PNG files under `frontend/public/agent-avatars/`.
2. Change `backend/app/services/seed.py` builtin avatar values to those public image paths.
3. Add a backend regression assertion for builtin avatar URLs and seed refresh.
4. Update `AgentAvatar` to render image URLs and fall back to text initials.
5. Replace direct `agent.avatar` text spans with `AgentAvatar`.
6. Adjust avatar CSS for image fills in list, chat, mention, and management surfaces.

## Tests

- Run focused backend API tests for agent seed behavior.
- Run frontend build.
- Run a browser smoke check for visible builtin image avatars.

## Out of Scope

- Changing agent names, capabilities, prompts, platform binding, or custom avatar creation behavior.
- Adding upload/cropping UI for custom agents.
