# M5 Custom Agent Avatar Upload Plan

## Goal

Use the provided default custom-agent image as the create-agent default avatar and support user-uploaded custom avatar images.

## Scope

- Add the provided default custom agent image as a frontend public asset.
- Update the create-agent modal avatar control from short text input to image preview plus upload/reset controls.
- Store uploaded images as resized data URLs in `Agent.avatar`.
- Keep text/emoji/custom URL avatar rendering support intact.
- Widen backend avatar storage from short `String` to `Text`.

## Contract Notes

- `docs/API_SPEC.md` and `packages/shared/types.ts` were reviewed.
- `Agent.avatar` already allows `emoji 或图片 URL`; data URLs are still string image references for frontend rendering.
- No REST route shape or shared type change is needed.

## Implementation Steps

1. Add `default_custom_agent.png` under `frontend/public/agent-avatars/`.
2. Change create-agent modal default avatar to `/agent-avatars/default_custom_agent.png`.
3. Add an upload control that accepts images, resizes them client-side, and writes a data URL to the hidden `avatar` field.
4. Update `AgentAvatar` image detection to support data URLs.
5. Change backend `Agent.avatar` mapped column to `Text`.
6. Add or update tests for custom data URL avatar persistence.

## Tests

- Run focused backend API tests for custom agent creation.
- Run frontend build.
- Run a browser smoke check for default custom avatar preview and upload control.

## Out of Scope

- Server-side file upload storage or image CDN management.
- Image cropping UI beyond square cover preview.
