# M1_1 后端数据与 REST 基线 Checklist

## 文档

- [x] `docs/plans/M1_TOTAL_PLAN.md` 已创建。
- [x] `docs/plans/M1_1_PLAN.md` 已创建。
- [x] `docs/plans/M1_1_CHECKLIST.md` 已创建。

## 数据层

- [x] SQLAlchemy 模型包含 User、AgentPlatform、Agent、Conversation、Message、Artifact。
- [x] Alembic 初始迁移包含核心表结构。
- [x] 空库可创建核心表。
- [x] seed 后存在 `mock` 平台。
- [x] seed 后存在代码工匠、审查大师、文档专家。

## API

- [x] REST 成功响应统一包含 `success/data/error/timestamp`。
- [x] REST 错误响应统一包含 `success/data/error/timestamp`。
- [x] 列表接口返回 `items/total/page/pageSize`。
- [x] `GET /api/v1/agents` 返回内置 Agent，字段为 camelCase。
- [x] `POST /api/v1/conversations` 可创建会话。
- [x] `GET /api/v1/conversations` 可分页读取会话。
- [x] `GET /api/v1/conversations/{id}` 可读取详情。
- [x] `DELETE /api/v1/conversations/{id}` 可删除会话。
- [x] `POST /api/v1/conversations/{id}/messages` 可创建用户消息。
- [x] `GET /api/v1/conversations/{id}/messages` 可分页读取消息。

## Tests

- [x] Agent API 测试通过。
- [x] Conversation API 测试通过。
- [x] Message API 测试通过。
- [x] 错误响应格式测试通过。
- [x] `cd backend && pytest -q` 通过。

## 下一步

- [ ] 进入 M1_2：WebSocket + MockAdapter 流式闭环。
- [ ] 将 REST fallback 消息创建逻辑复用到 WS `send_message`。
- [ ] 让 MockAdapter 输出 `text_delta`、`artifact`、`team_note`、`done` 事件。
