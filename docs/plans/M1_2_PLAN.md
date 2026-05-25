# M1_2 WebSocket + MockAdapter 流式闭环计划

## 目标

让后端 WebSocket 从 echo 升级为可演示的 Mock 流式通道：客户端发送 `send_message` 后，后端持久化用户消息，调用 MockAdapter，并按 `API_SPEC.md` 推送 Agent 思考、文本片段、产物、团队活动和完成事件。

## 范围

- 覆盖 `TASK_BREAKDOWN.md`：
  - 1.4 WebSocket 服务端。
  - 1.5 MockAdapter 实现。
- 不覆盖：
  - 前端 WebSocket Hook 与渲染。
  - 真实 LLM/CLI Agent。
  - 完整 Orchestrator LLM 决策。

## 契约要点

- 客户端发送：
  - `{ "type": "send_message", "data": SendMessageDTO }`
  - `{ "type": "stop_generation", "data": { "messageId": UUID } }`
- 服务端推送：
  - `agent_thinking`
  - `text_delta`
  - `artifact`
  - `team_activity`
  - `message_done`
  - `error`
- WS 事件字段使用 camelCase，与 `packages/shared/types.ts` 保持一致。

## 实现步骤

- 新增 WS 自动化测试，覆盖完整 Mock 事件流。
- 增强 MockAdapter：输出文本 delta、代码文件事件、team note 和 done。
- 更新 WS handler：解析 `send_message`，校验 conversation，选择 Agent，创建 user/agent message，转发 Mock 事件。
- 将 `file_created` 事件转换为 `Artifact` 记录和 `artifact` WS 消息。
- 为未知消息类型、缺失会话和 adapter 错误返回 `error` WS 消息。

## 测试

- `cd backend && pytest -q`
- 覆盖场景：
  - WS `send_message` 收到完整事件流。
  - REST 消息历史能看到 WS 持久化的用户消息和 Agent 消息。
  - Artifact API 能查到 WS 生成的代码产物。
  - 不存在的 conversation 返回 `error`，不 echo。

## 非范围

- 不做前端展示。
- 不做真实多 Agent 并行调度。
- 不实现 `stop_generation` 的进程中断；本阶段只返回可恢复提示。
