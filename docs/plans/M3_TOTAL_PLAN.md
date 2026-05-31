# M3 真实 Agent 接入与 Orchestrator 增强总体实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development` (recommended) or `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> 范围：`docs/TASK_BREAKDOWN.md` 中 M3 的 `3.1 - 3.11`，并补齐 M3 依赖的 DeepSeek LLMProvider 基线。
> 设计基线：`docs/plans/M3_ORCHESTRATOR_PLANNER_DESIGN.md`、`docs/plans/M3_ORCHESTRATOR_COORDINATION_DESIGN.md`。
> 日期：2026-05-31。

## Goal

将 M2 的“规则路由 + Mock 串行执行”升级为可演示、可测试、可降级的 M3 多 Agent 协作闭环：

```text
用户消息
→ DeepSeek Planner 规划静态 DAG
→ 后端验证并推导批次
→ Codex / OpenCode / LLMProvider / Mock Adapter 执行
→ 同批最多 3 个任务并行，其中最多 1 个 write
→ Team Board 与 Project State 批次级刷新
→ WebSocket 完整状态快照与前端协作展示
```

## Architecture

M3 将现有 `backend/app/ws/handlers.py` 中的 M2 串行流程拆成小型服务：Planner 负责语义规划，Validator 和 Scheduler 负责确定性验证与批次推导，Runtime 负责队列、执行、取消和状态快照。Codex/OpenCode CLI 自主管理源码上下文，AgentHub 只通过轻量 `AgentHandoffEnvelope` 传递任务边界和协作信息。

## Tech Stack

- Backend: Python 3.11、FastAPI、SQLAlchemy 2.0 async、SQLite、WebSocket、asyncio subprocess
- Frontend: React 18、TypeScript、Zustand
- LLM: DeepSeek OpenAI-compatible API
- Agent platforms: Mock、LLMProvider、OpenCode CLI、Codex CLI

---

## 一、实施原则

### Contract-first

- 先同步 `packages/shared/types.ts` 和 `docs/API_SPEC.md`，再实现 API、WS、前端 Store 和 Adapter。
- 每个模块实施前创建独立 `<MODULE>_PLAN.md` 与 `<MODULE>_CHECKLIST.md`。
- 本文是总体编排，不替代各模块的测试先行执行计划。

### Mock-first

- 保留 `MockAdapter`，不得删除或绕过。
- Planner、Validator、Scheduler、Queue、Team Board、Project State 和状态推送必须能用 deterministic fake planner + MockAdapter 完成测试。
- 外部 DeepSeek API 与 CLI 不作为 CI 必需条件。

### 关键边界

- LLM 是 Planner 的唯一计划生成器。规则层只验证，不生成备用计划。
- Planner 最多自动重规划一次；再次非法则推送 recoverable error。
- 执行平台可按 Adapter 模块设计执行健康检查与降级，但不得改变 Planner 语义。
- Codex/OpenCode 默认不注入源码全文；CLI Agent 在受限目录中自主探索文件。
- M3 不实现动态 DAG、并行写合并、自动重试、断点续跑和 Agent Discussion。

---

## 二、实施模块总览

| 模块 | 覆盖任务 | 主责 | 目标 |
|---|---|---|---|
| `M3_0` 契约冻结与测试骨架 | M3 公共基线 | 组长 | 统一 shared types、API_SPEC、测试 fixture 和迁移边界 |
| `M3_1` DeepSeek 公共客户端与 LLMProvider | M2.8、M2.9 补齐 | 小马 | 提供 Planner 与 LLMProvider 共用的 OpenAI-compatible client |
| `M3_2` CLI Adapter、进程管理与降级 | 3.1 - 3.6 | 小马 | 调研并尝试接入 OpenCode/Codex，提供 AdapterFactory 与生命周期管理 |
| `M3_3` 协作持久化模型 | 3.9、3.10、3.11 基础 | 组长 | 新增 Team Board、Team Note、Project State、Orchestrator Run、Task Run |
| `M3_4` Project State 服务 | 3.10 | 组长 | Python 扫描、Git Inspector、增量摘要、GET API |
| `M3_5` Team Board 与 Team Notes | 3.9 | 组长 | 原子 Notes、批次合并、Board Patch、GET API |
| `M3_6` Snapshot 与 Handoff | 3.8 | 组长 + 小马协作 | read 副本、文件安全、轻量 AgentHandoffEnvelope |
| `M3_7` Planner、Validator 与 Scheduler | 3.7 | 组长 | Prompt、澄清、能力推荐、静态 DAG 校验和批次推导 |
| `M3_8` Runtime 队列、执行与状态快照 | 3.11 | 组长 | FIFO Run 队列、批次执行、取消、重连恢复、WS 完整快照 |
| `M3_9` 前端协作交互 | 3.11 前端集成 | 组长 | 展示 Planner 摘要、批次、问题、Agent 推荐、审批和 warning |
| `M3_10` 全链路联调与验收 | Day 12 验收 | 全员 | Mock-first 稳定闭环、可选 DeepSeek/CLI 烟测、文档交接 |

---

## 三、依赖与并行关系

```text
M3_0 契约冻结
├──→ M3_1 DeepSeek Client / LLMProvider ─────────┐
├──→ M3_2 CLI Adapter / ProcessPool ─────────────┤
├──→ M3_3 协作持久化模型                         │
│    ├──→ M3_4 Project State ───────┐            │
│    └──→ M3_5 Team Board ─────────┤            │
│                                  ├──→ M3_6 Snapshot / Handoff
│                                  │            │
└──────────────────────────────────┴──→ M3_7 Planner / Validator / Scheduler
                                                │
M3_1 + M3_2 + M3_4 + M3_5 + M3_6 + M3_7 ──────┤
                                                └──→ M3_8 Runtime / WS
                                                      └──→ M3_9 Frontend
                                                            └──→ M3_10 验收
```

可并行推进：

- 小马：`M3_1 → M3_2`
- 组长：`M3_0 → M3_3 → (M3_4 || M3_5) → M3_6 → M3_7 → M3_8 → M3_9`
- 洋芋：按 M4 Artifact 线独立推进；M3 只定义 Artifact 事件兼容边界。

---

## 四、模块详细说明

## M3_0 契约冻结与测试骨架

### 目标

在实现前一次性冻结 M3 需要的 TypeScript 契约、API 文档、Python schema 和测试 fixture，避免后续模块重复改协议。

### 主要文件

- 修改：`packages/shared/types.ts`
- 修改：`docs/API_SPEC.md`
- 新增：`backend/app/schemas/orchestrator.py`
- 新增：`backend/tests/test_m3_contracts.py`
- 修改：`backend/tests/conftest.py`
- 新增：`docs/plans/M3_0_CONTRACTS_PLAN.md`
- 新增：`docs/plans/M3_0_CONTRACTS_CHECKLIST.md`

### 契约范围

- `Task.dependsOn` 从单值改为 `string[]`。
- 新增任务契约：`title`、`objective`、`acceptanceCriteria`、`constraints`、`accessMode`、`priority`、`riskHints`。
- 新增 `PlannerContext`、`PlannerResult`、`PlanningQuestion`、`RecommendedAgent`。
- 新增 `AgentHandoffEnvelope`、`TaskResult` 文件审计字段。
- 新增 `TeamBoard`、原子 `TeamNote`、结构化 `ProjectState`。
- 新增 `OrchestratorRunStatus`、`BatchStatus` 和完整 `WSOrchestratorStatus`。
- 新增 WS：规划问题、Agent 推荐、风险确认、共享状态刷新和用户响应。

### Test-first

- 先写 Pydantic schema 解析测试，覆盖四类 Planner 输出。
- 写失败测试验证非法 `dependsOn`、非法 `accessMode` 和缺失验收条件会被拒绝。
- 更新 API_SPEC 示例后，用 grep 检查旧的单值 `dependsOn` 示例全部移除。

### 验收

- `packages/shared/types.ts` 与 `docs/API_SPEC.md` 对齐。
- Python schema 可以解析合法样例并拒绝非法样例。
- 前端暂不需要行为变化，但 `npm run build` 必须保持通过。

---

## M3_1 DeepSeek 公共客户端与 LLMProvider

### 目标

提供 Planner、Board Summarizer、Project State Summarizer 和 LLMProviderAdapter 共用的 DeepSeek OpenAI-compatible 客户端。统一超时、有限重试、JSON 输出和 token usage 记录。

### 主要文件

- 修改：`backend/app/config.py`
- 新增：`backend/app/services/llm_client.py`
- 修改：`backend/app/adapters/llm_provider.py`
- 新增：`backend/tests/test_m3_llm_client.py`
- 新增：`backend/tests/test_m3_llm_provider.py`
- 新增：`docs/plans/M3_1_DEEPSEEK_CLIENT_PLAN.md`
- 新增：`docs/plans/M3_1_DEEPSEEK_CLIENT_CHECKLIST.md`

### 实现要点

- 将代码中的 Volcano 默认配置迁移为 backend-only DeepSeek 配置。
- 不修改 `.env` 凭据，不向前端返回 API Key。
- 使用可注入 transport，测试中不访问真实网络。
- 支持普通 JSON 请求和流式文本请求。
- 保存模型、耗时、真实 token usage 和错误类别。
- API Key 缺失或调用失败时返回明确错误，不伪造 Planner 结果。

### Test-first

- Fake transport 测试 JSON 响应、流式 delta、超时、一次有限重试和 usage 记录。
- LLMProvider 测试缺少 Key、成功事件流和错误事件。

### 验收

- CI 不依赖真实 DeepSeek API。
- 手动配置 Key 后可选运行真实 health check。
- Planner 与 LLMProvider 可以复用同一 client。

---

## M3_2 CLI Adapter、进程管理与降级

### 目标

调研并尝试完成 OpenCode 与 Codex CLI 接入；实现统一进程生命周期、超时终止、健康检查和 AdapterFactory。CLI 不可行时记录结论并稳定降级。

### 主要文件

- 修改：`backend/app/adapters/opencode.py`
- 修改：`backend/app/adapters/codex.py`
- 修改：`backend/app/services/agent_manager.py`
- 新增：`backend/app/services/process_pool.py`
- 新增：`backend/tests/test_m3_process_pool.py`
- 新增：`backend/tests/test_m3_agent_manager.py`
- 新增：`docs/CLI_AGENT_RESEARCH.md`
- 新增：`docs/plans/M3_2_CLI_ADAPTERS_PLAN.md`
- 新增：`docs/plans/M3_2_CLI_ADAPTERS_CHECKLIST.md`

### 实现要点

- OpenCode：调研 stdin/API/session 能力、结构化输出和停止方式。
- Codex：调研 full-auto 或 one-shot 模式、结构化输出和进程终止方式。
- `ProcessPool` 管理启动、并发、超时、取消、异常回收和日志截断。
- `AgentManagerService` 根据平台获取 Adapter，并暴露健康检查和执行接口。
- Adapter 保持业务无关：只接收 `workDir`、instruction 和 handoff context。
- 平台不可用时执行层可按配置降级；降级不改变 Planner 输出。

### Test-first

- 使用短命令 fake process 测试正常输出、超时、取消和异常退出。
- 使用 fake adapter 测试健康检查和降级选择。
- 不把本机已安装 CLI 作为 CI 前提。

### 验收

- `docs/CLI_AGENT_RESEARCH.md` 明确记录 OpenCode/Codex 的成功接入方式或不可行原因。
- CLI 可用时能够产出标准 `AgentEvent`。
- CLI 不可用时 Demo 仍可走 LLMProvider 或 Mock。

---

## M3_3 协作持久化模型

### 目标

为 Team Board、Team Notes、Project State、Orchestrator Run 和 Task Run 建立持久化基线，使断线恢复、队列、审计和 GET API 有可靠数据来源。

### 主要文件

- 新增：`backend/app/models/team_board.py`
- 新增：`backend/app/models/team_note.py`
- 新增：`backend/app/models/project_state.py`
- 新增：`backend/app/models/orchestrator_run.py`
- 新增：`backend/app/models/task_run.py`
- 修改：`backend/app/models/__init__.py`
- 新增：`backend/alembic/versions/<revision>_m3_orchestrator_state.py`
- 新增：`backend/tests/test_m3_models.py`
- 新增：`docs/plans/M3_3_PERSISTENCE_PLAN.md`
- 新增：`docs/plans/M3_3_PERSISTENCE_CHECKLIST.md`

### 数据边界

- `TeamBoard`：每个 conversation 一条快照，包含 version 和 JSON 聚合字段。
- `TeamNote`：独立原子记录，支持定向投递、状态迁移和注入审计。
- `ProjectState`：每个 conversation 一条事实快照和摘要。
- `OrchestratorRun`：消息级 Run、FIFO 队列、最新完整状态快照、澄清和 warning。
- `TaskRun`：任务级状态、批次、Agent、访问模式、审计结果和错误。

### Test-first

- 写模型创建、唯一约束、JSON 默认值和关联 conversation 的测试。
- 运行 Alembic upgrade，验证空库可以完整迁移。

### 验收

- 新模型可持久化并查询。
- 数据结构足以恢复 Run 最新状态快照。
- 不在模型中保存 API Key 或敏感文件内容。

---

## M3_4 Project State 服务

### 目标

实现 `WorkspaceScanner + GitInspector + ProjectStateSummarizer`，为 Planner 和 Handoff 提供紧凑、可降级的项目事实。

### 主要文件

- 修改：`backend/app/services/project_state.py`
- 新增：`backend/app/services/workspace_scanner.py`
- 新增：`backend/app/services/git_inspector.py`
- 新增：`backend/app/api/orchestrator.py`
- 修改：`backend/app/api/router.py`
- 新增：`backend/tests/test_m3_project_state.py`
- 新增：`docs/plans/M3_4_PROJECT_STATE_PLAN.md`
- 新增：`docs/plans/M3_4_PROJECT_STATE_CHECKLIST.md`

### 实现要点

- 扫描安全相对路径、大小和 mtime，计算 fingerprint。
- 排除 `.git/`、`node_modules/`、缓存、构建目录、敏感文件和越界软链接。
- 允许 `.env.example`。
- 完整安全路径最多保存 `5000` 条，Planner 默认最多接收 `500` 条代表路径。
- Git Inspector 读取仓库状态、branch、HEAD、最近 5 条 commit、status 和 diff stat。
- Git 超时或非 Git 目录时正常降级。
- DeepSeek 摘要失败时保留旧摘要并附加 warning，不阻塞执行。
- 提供 `GET /api/v1/conversations/{id}/project-state`。

### Test-first

- 临时目录测试敏感文件过滤、软链接越界、截断和 fingerprint。
- 临时 Git 仓库测试 branch、HEAD、dirty 和 recent commits。
- fake summarizer 测试成功更新和失败保留旧摘要。
- API 测试读取 Project State。

### 验收

- 首次规划前可以初始化扫描。
- Batch 开始可冻结 version，Batch 结束可增量刷新。
- PlannerContext 能获得精简项目摘要。

---

## M3_5 Team Board 与 Team Notes

### 目标

实现会话级 Team Board、原子 Team Notes、批次屏障合并和 Board Summarizer Patch。

### 主要文件

- 修改：`backend/app/services/team_protocol.py`
- 修改：`backend/app/api/orchestrator.py`
- 新增：`backend/tests/test_m3_team_protocol.py`
- 新增：`docs/plans/M3_5_TEAM_PROTOCOL_PLAN.md`
- 新增：`docs/plans/M3_5_TEAM_PROTOCOL_CHECKLIST.md`

### 实现要点

- Team Board 使用“单个快照 + 独立原子 Notes”。
- Note 类型：`decision | standard | heads_up | question | answer`。
- Note 状态：`active | resolved | superseded | archived`。
- 每个任务最多接受 `10` 条 Notes，单条最多 `1000` 字符。
- 根据类型、目标、标准化内容和 relatedFiles 计算指纹去重。
- 并行 Agent 只提交 Notes，不直接修改 Team Board。
- 批次结束时统一合并，Progress 由真实 TaskRun 状态更新。
- DeepSeek Board Summarizer 只提出 Patch；失败时保存 Notes 和真实 Progress，不阻塞执行。
- 冲突决策标记为 `review_required`，不得静默覆盖。
- 提供 `GET /api/v1/conversations/{id}/team-board`。

### Test-first

- 测试 Note 原子化、定向投递、去重、question/answer 关闭和 supersede。
- 测试失败任务只能提交 `heads_up` 和 `question`。
- 测试 summarizer 失败时 deterministic merge 仍成功。
- API 测试读取 Team Board。

### 验收

- 下一批 Agent 的 Handoff 可以筛选最多 `20` 条相关 Notes。
- Notes 注入后增加审计计数，但不自动消费。
- 前端可读取最新 Board version。

---

## M3_6 Snapshot 与 Agent Handoff

### 目标

为简单并行建立一致性快照、read 临时副本、目录边界和轻量 Handoff。

### 主要文件

- 新增：`backend/app/services/workspace_snapshot.py`
- 新增：`backend/app/services/handoff_builder.py`
- 新增：`backend/app/services/token_estimator.py`
- 修改：`backend/app/adapters/base.py`
- 新增：`backend/tests/test_m3_workspace_snapshot.py`
- 新增：`backend/tests/test_m3_handoff_builder.py`
- 新增：`docs/plans/M3_6_HANDOFF_PLAN.md`
- 新增：`docs/plans/M3_6_HANDOFF_CHECKLIST.md`

### 实现要点

- Batch 开始时创建统一 snapshot ID。
- write 任务在真实 `workDir` 执行。
- 每个 read 任务获得独立临时副本，意外写入在任务结束后丢弃。
- 副本排除敏感目录、大体积依赖目录和越界软链接。
- Handoff 只包含任务契约、权限、Project State 摘要、Team Notes、依赖摘要和 navigationHints。
- CLI Agent 默认不注入源码全文。
- `navigationHints` 只作建议，不限制 CLI 自主读取非敏感文件。
- Envelope 使用字符启发式 `TokenEstimator`：软目标 `16K`，硬上限 `32K`。
- 纯 API Adapter 的 `ContentMaterializer` 作为独立兼容路径，可后续增强。

### Test-first

- 测试多个 read 副本来自同一快照且相互隔离。
- 测试 read 副本修改不会影响真实项目。
- 测试 Handoff 超过预算时按顺序压缩低优先级内容。
- 测试安全规则和 manifest warning。

### 验收

- 同批 read/write 并行时，read Agent 只看到批次开始状态。
- CLI Adapter 可以接收统一 Handoff 并自主探索目录。

---

## M3_7 Planner、Validator 与 Scheduler

### 目标

实现 DeepSeek Planner Prompt、四类 PlannerResult、一次自动重规划、静态 DAG 校验和确定性批次推导。

### 主要文件

- 新增：`backend/app/services/orchestrator_planner.py`
- 新增：`backend/app/services/orchestrator_validator.py`
- 新增：`backend/app/services/orchestrator_scheduler.py`
- 新增：`backend/app/services/planner_prompt.py`
- 新增：`backend/tests/test_m3_planner.py`
- 新增：`backend/tests/test_m3_validator.py`
- 新增：`backend/tests/test_m3_scheduler.py`
- 新增：`docs/plans/M3_7_PLANNER_PLAN.md`
- 新增：`docs/plans/M3_7_PLANNER_CHECKLIST.md`

### 实现要点

- Planner 使用版本化 Prompt，例如 `planner-v1`。
- 输出：`ready | needs_clarification | capability_gap | cannot_plan`。
- 未指定 Agent 时，根据 capabilities 从当前参与者自动选择。
- 参与者能力不足时，从全局精简目录推荐 Agent，不自动加入会话。
- 澄清每轮建议最多 `6` 个问题、硬上限 `10` 个，最多 `5` 轮。
- 每个可选问题提供预设项、一个推荐项和自由补充入口。
- Validator 检查 Schema、Graph、Agent、Policy。
- Scheduler 使用拓扑排序推导批次：最多 `16` 个任务、`8` 个批次、每批最多 `3` 个任务、最多 `1` 个 write、同 Agent 同批最多 `1` 个任务。
- 两个独立 write 不强行增加语义依赖，由 Scheduler 分到不同批次。

### Test-first

- Fake Planner 测试四类结果。
- Validator 测试重复 ID、未知依赖、自引用、循环依赖、非参与 Agent 和超限。
- Scheduler 测试简单并行、write 资源限制、priority 排序、失败 blocked 传播。
- 测试首次非法自动重规划一次，二次非法停止。

### 验收

- Planner 只生成计划，规则层不改写计划。
- 批次推导稳定、快速、可复现。
- CI 不依赖真实 DeepSeek API。

---

## M3_8 Runtime 队列、执行与状态快照

### 目标

将 M2 的单请求串行处理升级为持久化 Run Runtime：支持 FIFO 队列、批次并行、取消、warning 完成态、失败隔离和断线恢复。

### 主要文件

- 重构：`backend/app/services/orchestrator.py`
- 新增：`backend/app/services/orchestrator_runtime.py`
- 新增：`backend/app/services/orchestrator_queue.py`
- 修改：`backend/app/ws/handlers.py`
- 修改：`backend/app/ws/manager.py`
- 新增：`backend/tests/test_m3_orchestrator_runtime.py`
- 新增：`backend/tests/test_m3_websocket_runtime.py`
- 新增：`docs/plans/M3_8_RUNTIME_PLAN.md`
- 新增：`docs/plans/M3_8_RUNTIME_CHECKLIST.md`

### 实现要点

- 同一 conversation 同时只允许一个 active Run。
- 新消息正常持久化并创建 queued Run，按 FIFO 自动启动。
- 每个 conversation 最多排队 `10` 条，超限时推送 recoverable error。
- Runtime 按 Scheduler 批次启动任务，使用 `asyncio.gather` 收集同批结果。
- 单任务失败时，无依赖任务继续；依赖失败任务的下游标记 `blocked`。
- `stop_generation` 取消当前整个 Run，不自动清空后续队列。
- Run 每次状态变化保存完整快照和递增 `sequence`。
- Team Board 或 Project State 刷新失败时 Run 仍为 `completed`，但带 warning。
- WebSocket 重连后立即推送当前 Run 最新快照。
- `reasoningSummary` 和批次安排进入聊天流展示。

### 状态

```text
queued
→ planning
→ awaiting_input
→ validating
→ replanning
→ awaiting_approval
→ executing
→ summarizing
→ completed | failed | cancelled
```

### Test-first

- 测试单会话 FIFO 队列和队列上限。
- 测试同批最多一个 write、最多三个任务并发。
- 测试失败 blocked 传播、取消整个 Run、warning 完成态。
- WS 测试完整快照 sequence 单调递增。
- WS 测试断线重连后立即恢复最新快照。

### 验收

- MockAdapter 下可稳定跑通多批次并行执行。
- Runtime 不依赖单个 WebSocket 连接存活。
- 队列和状态可从持久化快照恢复。

---

## M3_9 前端协作交互

### 目标

让用户在聊天工作台中理解 Planner 的决策、回答问题、确认推荐 Agent、审批风险操作，并在重连后恢复当前协作进度。

### 主要文件

- 新增：`frontend/src/stores/orchestratorStore.ts`
- 修改：`frontend/src/hooks/useWebSocket.ts`
- 修改：`frontend/src/services/websocket.ts`
- 修改：`frontend/src/components/cards/OrchestratorStatus.tsx`
- 新增：`frontend/src/components/cards/OrchestratorInputCard.tsx`
- 新增：`frontend/src/components/cards/OrchestratorApprovalCard.tsx`
- 修改：`frontend/src/components/chat/ChatArea.tsx`
- 修改：`frontend/src/components/chat/MessageBubble.tsx`
- 新增：`frontend/src/components/chat/TeamBoardPanel.tsx`
- 新增：`frontend/src/services/orchestratorApi.ts`
- 新增：`docs/plans/M3_9_FRONTEND_PLAN.md`
- 新增：`docs/plans/M3_9_FRONTEND_CHECKLIST.md`

### 实现要点

- 新 Store 按 conversation 保存最新 Run 快照、sequence、问题、审批、queue position 和 warning。
- 只接受 sequence 更新的状态，忽略旧快照。
- 展示 Planner 的简短 `reasoningSummary` 和批次安排。
- `needs_clarification` 卡片支持选项、推荐标签和自由补充输入。
- `capability_gap` 卡片展示推荐 Agent，用户确认后再加入会话。
- elevated write 操作展示风险原因和确认按钮。
- RuntimeBanner 展示 queued、running、blocked、warning 和 completed。
- GET API 加载 Team Board 与 Project State 摘要。

### Test-first / 验证

- 为 Store 提取纯 reducer 或 helper，测试 sequence 去重和响应 payload。
- 运行 `npm run lint` 和 `npm run build`。
- 浏览器烟测 queued、澄清、审批、并行状态和重连恢复。

### 验收

- 用户可以完成“提出需求 → 回答 Planner 问题 → 确认 Agent 推荐 → 查看批次执行 → 查看 warning”的交互。
- 不向普通 UI 暴露 `platformId`。

---

## M3_10 全链路联调与验收

### 目标

完成 Day 12 验收，形成 Mock-first 稳定闭环，并记录真实 DeepSeek 和 CLI Agent 的可选联调结论。

### 主要文件

- 新增：`backend/tests/test_m3_e2e.py`
- 更新：`docs/plans/M3_TOTAL_CHECKLIST.md`
- 更新：`DEVLOG.md`
- 按联调结果更新：`docs/API_SPEC.md`
- 按调研结果更新：`docs/CLI_AGENT_RESEARCH.md`

### 必测场景

1. 用户群聊发送请求，Planner 自动选择参与 Agent 并生成多个任务。
2. 两个无依赖 read 与一个 write 在同批执行，read 使用隔离副本。
3. 后续 read 任务依赖前序 write，能够读取新文件。
4. Planner 首次非法，收到错误后自动重规划成功。
5. Planner 二次非法，推送 recoverable error。
6. Planner 请求澄清，用户回答后继续规划。
7. Planner 发现能力缺口，用户确认加入 Agent 后继续规划。
8. 当前 Run 执行时再次发消息，新消息进入队列并在前序完成后启动。
9. 单任务失败，无依赖任务继续，下游任务变为 blocked。
10. `stop_generation` 取消整个当前 Run，队列后续消息仍保留。
11. Team Board 和 Project State 更新失败时 Run completed with warning。
12. WS 断线重连后立即收到最新状态快照。

### 验证命令

```bash
cd backend && pytest -q
cd frontend && npm run lint
cd frontend && npm run build
```

可选手动烟测：

```text
DeepSeek API health check
OpenCode CLI smoke
Codex CLI smoke
前端浏览器端到端演示
```

### 验收

- 群聊请求可以由 DeepSeek Planner 拆解，并在 MockAdapter 下稳定执行。
- Team Board 与 Project State 可读取。
- CLI Agent 接入结论明确：成功可用，或记录不可行原因并稳定降级。
- 前端可以展示实时协作状态、队列、问题、审批和 warning。
- 文档、checklist 和 DEVLOG 完整更新。

---

## 五、实现阶段文件映射

### Shared Contract

- `packages/shared/types.ts`
- `docs/API_SPEC.md`
- `backend/app/schemas/orchestrator.py`

### Backend Models

- `backend/app/models/team_board.py`
- `backend/app/models/team_note.py`
- `backend/app/models/project_state.py`
- `backend/app/models/orchestrator_run.py`
- `backend/app/models/task_run.py`
- `backend/alembic/versions/<revision>_m3_orchestrator_state.py`

### Backend Services

- `backend/app/services/llm_client.py`
- `backend/app/services/process_pool.py`
- `backend/app/services/project_state.py`
- `backend/app/services/workspace_scanner.py`
- `backend/app/services/git_inspector.py`
- `backend/app/services/team_protocol.py`
- `backend/app/services/workspace_snapshot.py`
- `backend/app/services/handoff_builder.py`
- `backend/app/services/token_estimator.py`
- `backend/app/services/orchestrator_planner.py`
- `backend/app/services/orchestrator_validator.py`
- `backend/app/services/orchestrator_scheduler.py`
- `backend/app/services/orchestrator_runtime.py`
- `backend/app/services/orchestrator_queue.py`
- `backend/app/services/orchestrator.py`

### Adapter Integration

- `backend/app/adapters/base.py`
- `backend/app/adapters/llm_provider.py`
- `backend/app/adapters/opencode.py`
- `backend/app/adapters/codex.py`
- `backend/app/services/agent_manager.py`

### Backend API / WS

- `backend/app/api/orchestrator.py`
- `backend/app/api/router.py`
- `backend/app/ws/handlers.py`
- `backend/app/ws/manager.py`

### Frontend

- `frontend/src/stores/orchestratorStore.ts`
- `frontend/src/hooks/useWebSocket.ts`
- `frontend/src/services/websocket.ts`
- `frontend/src/services/orchestratorApi.ts`
- `frontend/src/components/cards/OrchestratorStatus.tsx`
- `frontend/src/components/cards/OrchestratorInputCard.tsx`
- `frontend/src/components/cards/OrchestratorApprovalCard.tsx`
- `frontend/src/components/chat/ChatArea.tsx`
- `frontend/src/components/chat/MessageBubble.tsx`
- `frontend/src/components/chat/TeamBoardPanel.tsx`

---

## 六、里程碑验收

### Checkpoint A：契约与持久化

- Shared types 和 API_SPEC 对齐。
- Alembic 可从空库升级。
- Team Board、Team Note、Project State、Orchestrator Run、Task Run 可持久化。

### Checkpoint B：协作状态

- Project State 扫描和 Git Inspector 可降级运行。
- Team Notes 可以原子化、去重、定向注入和合并。
- read 副本隔离可验证。

### Checkpoint C：Planner 与 Runtime

- Fake Planner 下四类输出可运行。
- Validator 拒绝非法计划。
- Scheduler 稳定推导简单并行批次。
- Run 队列、失败隔离、取消和断线恢复可测试。

### Checkpoint D：Day 12 演示

- 群聊发送请求。
- Planner 摘要和批次安排显示。
- 多 Agent 简单并行执行。
- Team Activity 和共享状态更新。
- 队列、澄清、审批和 warning 交互可演示。

---

## 七、Out of Scope

- 动态插入 DAG 任务。
- 并行 write 冲突合并。
- 自动重试与失败补偿。
- 任务断点续跑。
- Agent Discussion 多轮仲裁。
- 向量数据库和重型源码上下文引擎。
- M4 Artifact Preview、Diff 卡片和 Monaco 增强。
- P2 部署、移动端和复杂权限系统。
