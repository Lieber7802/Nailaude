# M3 真实 Agent 接入与 Orchestrator 增强总体 Checklist

> 对应计划：`docs/plans/M3_TOTAL_PLAN.md`
> 设计基线：`docs/plans/M3_ORCHESTRATOR_PLANNER_DESIGN.md`、`docs/plans/M3_ORCHESTRATOR_COORDINATION_DESIGN.md`

## Docs

- [x] Planner v1.0 设计已沉淀。
- [x] 协作上下文、Team Board、Project State、OrchestratorStatus v1.0 设计已沉淀。
- [x] `M3_TOTAL_PLAN.md` 已创建。
- [x] `M3_TOTAL_CHECKLIST.md` 已创建。
- [x] 每个实施模块开始前创建对应子计划和 checklist。
- [x] M3 完成后更新 `DEVLOG.md`。

## M3_0 契约冻结与测试骨架

- [x] 更新 `packages/shared/types.ts` 中的 Task、Planner、Handoff、Team Protocol、Project State 和 WS 类型。
- [x] 同步更新 `docs/API_SPEC.md`。
- [x] 新增 `backend/app/schemas/orchestrator.py`。
- [x] 为四类 PlannerResult 编写 schema 测试。
- [x] 验证非法依赖、非法 accessMode 和缺失验收条件会被拒绝。
- [x] 运行前端构建确认共享类型可用。

## M3_1 DeepSeek 公共客户端与 LLMProvider

- [x] 将运行时代码中的默认 LLM 后端调整为 DeepSeek OpenAI-compatible 配置。
- [x] 不修改 `.env` 中的 API Key 或凭据。
- [x] 新增可注入 transport 的 `llm_client.py`。
- [x] 实现 JSON 请求、流式 delta、超时、有限重试和 usage 记录。
- [x] 完成 `LLMProviderAdapter`。
- [x] Fake transport 测试通过。
- [x] 可选真实 DeepSeek health check 结论已记录。

## M3_2 CLI Adapter、进程管理与降级

- [x] 调研 OpenCode CLI 的调用、结构化输出、停止和 session 能力。
- [x] 调研 Codex CLI 的调用、结构化输出、停止和 one-shot 能力。
- [x] 新增 `ProcessPool`。
- [x] 测试正常退出、超时、取消和异常回收。
- [x] 完成 `AgentManagerService` AdapterFactory。
- [x] 测试健康检查和执行层降级。
- [x] 更新 `docs/CLI_AGENT_RESEARCH.md`。

## M3_3 协作持久化模型

- [x] 新增 Team Board 模型。
- [x] 新增 Team Note 模型。
- [x] 新增 Project State 模型。
- [x] 新增 Orchestrator Run 模型。
- [x] 新增 Task Run 模型。
- [x] 新增 Alembic migration。
- [x] 空库 Alembic upgrade 通过。
- [x] 模型创建、默认值和唯一约束测试通过。

## M3_4 Project State

- [x] 实现安全 WorkspaceScanner。
- [x] 过滤敏感文件、依赖目录、缓存、构建目录和越界软链接。
- [x] 允许读取 `.env.example`。
- [x] 安全路径最多保存 `5000` 条，Planner 最多接收 `500` 条。
- [x] 实现 GitInspector，设置短超时并支持非 Git 降级。
- [x] 实现增量摘要；DeepSeek 失败时保留旧摘要并记录 warning。
- [x] 实现 `GET /api/v1/conversations/{id}/project-state`。
- [x] 单元测试和 API 测试通过。

## M3_5 Team Board 与 Team Notes

- [x] 实现单快照 Team Board。
- [x] 实现原子 Team Notes。
- [x] 支持 decision、standard、heads_up、question、answer。
- [x] 支持 active、resolved、superseded、archived。
- [x] 实现 Note 指纹去重。
- [x] 实现 question/answer 关闭。
- [x] 实现批次屏障确定性合并。
- [x] 实现 Board Summarizer Patch；失败不阻塞执行。
- [x] 冲突决策标记为 `review_required`。
- [x] 实现 `GET /api/v1/conversations/{id}/team-board`。
- [x] 单元测试和 API 测试通过。

## M3_6 Snapshot 与 Handoff

- [x] 实现统一 Batch snapshot ID。
- [x] 为每个 read 任务创建独立临时副本。
- [x] 验证 read 副本修改不会影响真实项目。
- [x] write 任务只在真实 `workDir` 执行。
- [x] 实现 AgentHandoffEnvelope Builder。
- [x] CLI Agent 默认不注入源码全文。
- [x] navigationHints 仅作为建议。
- [x] 实现字符启发式 TokenEstimator。
- [x] Handoff 软目标 `16K`、硬上限 `32K`。
- [x] 实现 manifest warning。
- [x] 单元测试通过。

## M3_7 Planner、Validator 与 Scheduler

- [x] 新增版本化 `planner-v1` Prompt。
- [x] 支持 `ready`。
- [x] 支持 `needs_clarification`。
- [x] 支持 `capability_gap`。
- [x] 支持 `cannot_plan`。
- [x] 支持根据 capabilities 从参与者自动选择 Agent。
- [x] 支持从精简全局目录推荐 Agent，不自动加入会话。
- [x] 澄清问题包含选项、推荐项和自由补充入口。
- [x] 实现 Schema、Graph、Agent、Policy 校验。
- [x] Planner 非法时最多自动重规划一次。
- [x] 实现拓扑排序批次推导。
- [x] 限制最多 `16` 个任务、`8` 个批次、每批 `3` 个任务、最多 `1` 个 write。
- [x] Validator 和 Scheduler 测试通过。

## M3_8 Runtime 队列、执行与状态快照

- [x] 同一 conversation 只允许一个 active Run。
- [x] 新消息创建 queued Run。
- [x] FIFO 队列自动启动。
- [x] 每个 conversation 队列上限为 `10`。
- [x] Runtime 使用批次级并行执行。
- [x] 单任务失败时，无依赖任务继续。
- [x] 失败任务下游标记为 blocked。
- [x] `stop_generation` 取消整个当前 Run。
- [x] 取消当前 Run 时不自动清空后续队列。
- [x] 状态快照 sequence 单调递增。
- [x] Team Board / Project State 刷新失败时 completed with warning。
- [x] WebSocket 重连后立即推送最新状态快照。
- [x] Runtime 和 WS 测试通过。

## M3_9 前端协作交互

- [x] 新增 `orchestratorStore.ts`。
- [x] Store 忽略旧 sequence 状态快照。
- [x] useWebSocket 处理完整状态快照。
- [x] 展示 Planner reasoningSummary 和批次安排。
- [x] 展示 queued 状态和队列位置。
- [x] 实现澄清问题卡片。
- [x] 每个可选问题显示推荐项和自由补充输入。
- [x] 实现 capability gap Agent 推荐卡片。
- [x] 实现 elevated write 审批卡片。
- [x] 展示 blocked、warning 和 completed。
- [x] 加载 Team Board 和 Project State GET API。
- [x] 不向普通 UI 暴露 `platformId`。
- [x] `npm run lint` 通过。
- [x] `npm run build` 通过。

## M3_10 全链路联调与验收

- [x] 群聊请求由 Planner 自动拆解并选择参与 Agent。
- [x] 同批一个 write 与多个 read 并行运行。
- [x] read Agent 使用隔离副本。
- [x] 后续依赖任务读取前序 write 新结果。
- [x] 首次非法计划自动重规划成功。
- [x] 二次非法计划推送 recoverable error。
- [x] 澄清回答后 Planner 恢复运行。
- [x] 用户确认推荐 Agent 后 Planner 恢复运行。
- [x] 新消息在 active Run 期间进入队列。
- [x] 单任务失败不影响无依赖任务。
- [x] `stop_generation` 取消整个当前 Run。
- [x] 共享状态刷新失败时展示 warning。
- [x] WS 重连恢复最新快照。
- [x] Team Board 可读。
- [x] Project State 可读。
- [x] CLI 接入成功或降级结论明确记录。

## Verification

- [x] `cd backend && pytest -q`
- [x] `cd frontend && npm run lint`
- [x] `cd frontend && npm run build`
- [x] Mock-first 浏览器端到端烟测完成。
- [x] 可选 DeepSeek API smoke 结论记录。
- [x] 可选 OpenCode CLI smoke 结论记录。
- [x] 可选 Codex CLI smoke 结论记录。
- [x] `DEVLOG.md` 已更新。
