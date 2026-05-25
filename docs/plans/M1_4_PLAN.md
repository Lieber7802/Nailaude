# M1_4 聊天流 + 代码卡片 + 全链路联调计划

## 目标

完成 M1 的可演示闭环：前端新建/选择会话，发送消息，通过 WebSocket 接收 Mock 流式回复，并在聊天流内展示代码卡片。

## 范围

- 覆盖 `TASK_BREAKDOWN.md`：
  - 1.9 聊天消息流基础版。
  - 1.10 代码卡片基础版。
  - 1.11 Mock 闭环联调。
- 不覆盖：
  - 完整 @ mention 浮层。
  - Monaco 编辑器。
  - Diff/Preview 完整交互。
  - 多 Agent Orchestrator 汇总。

## 契约要点

- 发送消息使用 WS `send_message`。
- 流式文本来自 WS `text_delta`。
- 代码卡片来自 WS `artifact` 中的 `Artifact.files`。
- REST message API 仅用于进入会话时加载历史。

## 实现步骤

- 实现 `MessageInput`：文本输入、发送按钮、默认 mention 当前第一个 Agent。
- 实现 `MessageBubble`：渲染 user/agent/team 文本和消息内 artifact。
- 实现 `CodeCard`：展示文件名、语言和代码内容。
- 增强 `ChatArea`：加载消息、展示消息流、挂载输入框。
- 增强 `PreviewPanel`：展示当前 active artifact 的摘要。
- 在 `Workspace` 中连接会话、Agent、WS send 和消息 store。

## 验证

- `cd frontend && npm run build`
- `cd backend && pytest -q`
- 启动后端和前端后，浏览器可完成：新建会话 -> 输入消息 -> 看到 Mock 流式回复 -> 看到代码卡片。

## 非范围

- 不要求视觉精修。
- 不要求移动端适配。
- 不要求真实 Agent 接入。
