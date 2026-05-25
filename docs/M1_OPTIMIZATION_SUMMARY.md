# M1 Optimization Summary

## 背景

本次优化来自 M1 完成后的严格 review。目标不是新增业务范围，而是把 M1 Mock-first 闭环从 happy path 加固成可继续承接 M2 的稳定基线。

## 修复内容

- 后端消息历史现在会返回已持久化的 artifacts，并补充 agent 消息的 `agentName`。
- REST 参数校验错误统一返回 `ApiResponse`，避免 422 走 FastAPI 默认格式。
- Conversation `type` 限制为 `single` / `group`，`workDir` 限制在项目 `workspaces/` 目录下。
- Message REST fallback 拒绝空内容。
- WebSocket 能处理 malformed JSON，异常路径会返回结构化 `error` 事件并清理连接。
- WebSocket 新增 `user_message` 下行事件，用 `clientMessageId` 帮前端把乐观消息替换为服务端真实消息。
- 前端 WebSocket client 增加 stale socket guard，旧连接事件不会覆盖新连接状态。
- 前端历史消息加载会 hydrate artifact store，刷新或切换会话后 CodeCard/PreviewPanel 能恢复。
- MockAdapter、seed 数据、工作台关键文案恢复为可读中文。
- 前端通过 npm `overrides` 将 transitive `dompurify` 提升到安全版本，消除 moderate audit 风险。

## 契约变化

- `packages/shared/types.ts` 增加 `WSUserMessage`，并将 `{ type: "user_message" }` 纳入 `WSServerMessage`。
- `docs/API_SPEC.md` 增加 `user_message` WebSocket 下行事件说明。
- 其他 REST 数据结构保持现有 `ApiResponse<T>` / `PaginatedResponse<T>` 约定。

## 测试与验证

- `cd backend && pytest -q`：8 passed。
- `cd frontend && npm run build`：TypeScript 与 Vite build 通过。
- `cd frontend && npm audit --audit-level=moderate`：found 0 vulnerabilities。

## 后续注意

- 当前 `workDir` 校验允许空字符串，保持与 M1 创建对话默认值兼容；真实 Agent 接入时应进一步统一 workdir 创建和存在性检查。
- 启动时 `Base.metadata.create_all()` 仍是开发便利逻辑，后续进入更正式环境前建议改为 Alembic 驱动。
- 旧本地开发数据库如果已经 seed 过乱码内置 Agent，可能仍保留旧数据；新库和测试库均会写入可读中文 seed。
