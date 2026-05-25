# M1_3 前端工作台基础壳计划

## 目标

搭出可交互的前端工作台基础壳：三栏布局、Agent/Conversation 数据加载、Zustand store、API client 和 WebSocket client/hook。M1_3 不负责完整聊天渲染和代码卡片，那些留给 M1_4。

## 范围

- 覆盖 `TASK_BREAKDOWN.md`：
  - 1.6 前端三栏布局。
  - 1.7 前端 Zustand Store。
  - 1.8 前端 WebSocket Hook。
- 不覆盖：
  - 完整 MessageBubble/CodeCard 渲染。
  - 复杂 @ mention 浮层。
  - Monaco/Diff/Preview 完整能力。

## 契约要点

- 前端 API client 解析后端统一 `ApiResponse<T>`。
- 前端本地类型字段使用 camelCase，与 `packages/shared/types.ts` 对齐。
- WebSocket client 分发 `WSServerMessage` 的 `type/data`，不处理业务 UI 细节。

## 实现步骤

- 增强 `services/api.ts`：封装 `ApiResponse<T>`，提供 agents/conversations/messages API。
- 增强 stores：Conversation、Message、Agent、Artifact store 支持列表加载和 WS 事件需要的写入操作。
- 增强 `services/websocket.ts`：连接状态、send、on/off、错误保护。
- 增强 `useWebSocket.ts`：订阅 `text_delta`、`artifact`、`message_done`、`team_activity` 并写入 store。
- 搭出 `Workspace` 三栏：左栏会话/Agent 信息，中栏聊天占位，右栏预览占位。

## 验证

- `cd frontend && npm run build`
- 浏览器打开工作台时应能看到三栏结构。
- 后端可用时，前端能请求 Agent 和 Conversation 列表。

## 非范围

- 不启动真实端到端聊天体验。
- 不做视觉精修。
- 不引入新前端依赖。
