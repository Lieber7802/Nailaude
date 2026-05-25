# M1_4 聊天流 + 代码卡片 + 全链路联调 Checklist

## Docs

- [x] `docs/plans/M1_4_PLAN.md` 已创建。
- [x] `docs/plans/M1_4_CHECKLIST.md` 已创建。

## Implementation

- [x] `MessageInput` 支持输入和发送。
- [x] `Workspace` 通过 WS 发送 `send_message`。
- [x] 用户消息发送后进入本地消息流。
- [x] `useWebSocket` 接收 `text_delta` 并更新消息流。
- [x] `useWebSocket` 接收 `artifact` 并写入 artifact store。
- [x] `MessageBubble` 渲染用户和 Agent 消息。
- [x] `MessageBubble` 渲染消息关联代码卡片。
- [x] `CodeCard` 展示文件名、语言和代码。
- [x] `PreviewPanel` 展示 active artifact 摘要。
- [x] 切换会话时加载历史消息。

## Verification

- [x] `cd frontend && npm run build` 通过。
- [x] `cd backend && pytest -q` 通过。
- [x] `DEVLOG.md` 已追加记录。
