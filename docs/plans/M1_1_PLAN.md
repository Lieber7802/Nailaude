# M1_1 后端数据与 REST 基线计划

## 目标

完成 M1 的第一批可验收任务：让后端数据模型、迁移、内置 seed 数据、基础 REST API 和自动化测试可用。M1_1 不触发 Agent、不实现 WebSocket 流式回复、不改前端页面。

## 范围

- 覆盖 `TASK_BREAKDOWN.md`：
  - 1.2 数据库 Schema 实现。
  - 1.3 REST API 骨架。
- 不覆盖：
  - 1.4 WebSocket 服务端。
  - 1.5 MockAdapter 完整事件流。
  - 1.6-1.11 前端与全链路联调。

## 实现要点

- REST 响应统一为 `ApiResponse<T>`：`success`、`data`、`error`、`timestamp`。
- 列表接口的 `data` 使用 `PaginatedResponse<T>`：`items`、`total`、`page`、`pageSize`。
- 后端内部和数据库使用 snake_case，对外 JSON 使用 `API_SPEC.md` 和 `packages/shared/types.ts` 中的 camelCase。
- 内置 seed 数据至少包含：
  - 平台：`mock`、`llm`、`opencode`、`codex`。
  - Agent：代码工匠、审查大师、文档专家。
- REST fallback 发送消息只持久化用户消息，不调用 Agent，不推送 WS。
- 删除内置 Agent 必须返回错误。

## API 验收接口

- `GET /api/v1/agents`
- `GET /api/v1/agents/{id}`
- `POST /api/v1/agents`
- `PATCH /api/v1/agents/{id}`
- `DELETE /api/v1/agents/{id}`
- `POST /api/v1/conversations`
- `GET /api/v1/conversations?page=1&pageSize=20&search=xxx`
- `GET /api/v1/conversations/{id}`
- `PATCH /api/v1/conversations/{id}`
- `DELETE /api/v1/conversations/{id}`
- `POST /api/v1/conversations/{id}/messages`
- `GET /api/v1/conversations/{id}/messages?page=1&pageSize=50`

## 测试计划

- 自动化测试为主：`cd backend && pytest -q`。
- 覆盖场景：
  - 空库中请求 Agent API 后存在内置 seed 数据。
  - 创建 group conversation 后，`participantIds` 和 `workDir` 按 camelCase 返回。
  - 会话列表支持分页和搜索。
  - REST fallback 发送消息后，只产生一条 `role=user` 消息。
  - 不存在的会话读取/发消息返回统一错误格式。
- 手动冒烟：
  - `uvicorn app.main:app --reload --port 8000`
  - `GET /health`
  - `GET /api/v1/agents`

## 交付边界

- 不修改 `packages/shared/types.ts`。
- 不新增真实 LLM/CLI 依赖。
- 不在 Adapter 层加入业务逻辑。
- 不暴露 `platformId` 到普通用户界面；本阶段仅 API 数据契约保留该字段。
