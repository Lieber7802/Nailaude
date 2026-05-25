# M1 Mock-first 完整闭环总计划

> 范围：`TASK_BREAKDOWN.md` 中 M1 的 1.1-1.11。  
> 目标：Day 4 结束时，不依赖任何外部 API/CLI，仅用 Mock 跑通核心产品流程。

## 阶段拆分

### M1_1 后端数据与 REST 基线

- 覆盖任务：1.2 数据库 Schema 实现、1.3 REST API 骨架。
- 目标：让模型、迁移、seed 数据、Conversation/Message/Agent REST API 和自动化测试先站稳。
- 交付物：SQLAlchemy 模型、Alembic 初始迁移、内置平台/Agent seed、统一 `ApiResponse<T>` 响应、pytest 覆盖。
- 验收：`cd backend && pytest -q` 通过；`/api/v1/agents`、`/api/v1/conversations`、`/api/v1/conversations/{id}/messages` 可用。
- 依赖：1.1 项目初始化。

### M1_2 WebSocket + MockAdapter 流式闭环

- 覆盖任务：1.4 WebSocket 服务端、1.5 MockAdapter 实现。
- 目标：WebSocket 接收 `send_message` 后调用 MockAdapter，并推送 `agent_thinking`、`text_delta`、`artifact`、`team_activity`、`message_done`。
- 交付物：WS handler、连接管理增强、MockAdapter 代码产物/Diff/TeamNote 事件、REST 与 WS 共用消息持久化。
- 验收：不依赖前端，通过 WS 客户端发送消息能收到完整 Mock 事件流。
- 依赖：M1_1 的 Message/Conversation 数据基线。

### M1_3 前端工作台基础壳

- 覆盖任务：1.6 前端三栏布局、1.7 Zustand Store、1.8 WebSocket Hook。
- 目标：搭出可交互工作台基础壳，前端能加载 Agent/Conversation，连接 WS，并把事件分发进 store。
- 交付物：三栏 Layout、Conversation/Message/Agent/Artifact stores、API client、WS client/hook。
- 验收：浏览器打开工作台无报错，可看到 Agent/会话基础数据，WS 连接状态可观察。
- 依赖：M1_1 REST API、M1_2 WS 协议。

### M1_4 聊天流 + 代码卡片 + 全链路联调

- 覆盖任务：1.9 聊天消息流、1.10 代码卡片、1.11 Mock 闭环联调。
- 目标：用户能在前端发送消息，看到流式回复和代码卡片。
- 交付物：MessageBubble、MessageInput、自动滚动、基础 CodeCard、Artifact 渲染分支、端到端联调。
- 验收：新建会话 -> 发送消息 -> Mock 流式回复 -> 代码卡片展示，全流程不依赖外部 API/CLI。
- 依赖：M1_1、M1_2、M1_3。

## M1 完成标准

- 前后端启动无报错。
- 前端能新建会话、发送消息。
- MockAdapter 返回流式文本和代码产物。
- 前端能渲染流式消息和代码卡片。
- WebSocket 连接稳定，断开后能给出可理解状态。
- 全流程只依赖本地 Mock，不依赖 OpenCode、Codex、火山方舟或 OpenAI。

## 推进原则

- 每个阶段都必须有独立验收方式，避免把联调风险堆到最后。
- 只改当前阶段需要的接口，不提前实现 P1/P2 功能。
- `packages/shared/types.ts` 和 `docs/API_SPEC.md` 是契约文件，修改时必须同步。
- MockAdapter 是永久组件，不允许删除或绕过。
