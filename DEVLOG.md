# DEVLOG — 开发会话沉淀日志

> 每次 AI 编码会话结束时，在本文件末尾追加一条记录。  
> 其他成员的 AI 读最近 3-5 条即可了解项目当前状态。

## 记录格式

```markdown
## [日期] 成员 - 任务编号 任务名称

### 完成内容
- 做了什么（1-3 条）

### 新增/修改文件
- `path/to/file` (新增/修改/删除)

### 接口变更
- 是否修改了 shared/types.ts 或 API_SPEC.md（如有，简述变更）

### 下一步
- 后续需要做什么

### 给其他成员的提醒
- @小马：xxx
- @洋芋：xxx
```

---

## [2026-05-21] 组长 - 项目初始化

### 完成内容
- 完成 PRD v1.6、TECH_DESIGN v1.1、API_SPEC v1.1、TASK_BREAKDOWN v1.0
- 定义共享类型 packages/shared/types.ts
- 建立 AI 协作规范 AGENTS.md、CLAUDE.md、CONTRIBUTING.md

### 新增/修改文件
- `docs/PRD.md` (新增)
- `docs/TECH_DESIGN.md` (新增)
- `docs/API_SPEC.md` (新增)
- `docs/TASK_BREAKDOWN.md` (新增)
- `packages/shared/types.ts` (新增)
- `AGENTS.md` (新增)
- `CLAUDE.md` (新增)
- `CONTRIBUTING.md` (新增)
- `DEVLOG.md` (新增)

### 接口变更
- 首次定义，无变更

### 下一步
- M1.1 项目初始化（Vite+React + FastAPI 脚手架）
- M1.2 数据库 Schema 实现

### 给其他成员的提醒
- @小马：Day 5 加入时先读 AGENTS.md → types.ts → DEVLOG 最近几条
- @洋芋：Day 8 加入时同上，重点看 Artifact 相关类型和 API_SPEC 第六章

## [2026-05-24] Codex - M1_1 后端数据与 REST 基线

### 完成内容
- 沉淀 M1 总计划、M1_1 实施计划和 M1_1 checklist 到 `docs/plans/`
- 实现 REST 统一响应、内置平台/Agent seed、Conversation/Message/Agent 基础 API
- 增加 pytest 覆盖 Agent seed、会话 CRUD、消息 REST 降级接口 和错误响应格式

### 新增/修改文件
- `docs/plans/M1_TOTAL_PLAN.md` (新增)
- `docs/plans/M1_1_PLAN.md` (新增)
- `docs/plans/M1_1_CHECKLIST.md` (新增)
- `backend/app/api/` (修改：REST 路由、响应工具、序列化)
- `backend/app/services/seed.py` (新增)
- `backend/tests/` (新增/修改)
- `backend/requirements.txt` (修改)

### 接口变更
- 未修改 `packages/shared/types.ts` 或 `docs/API_SPEC.md`
- 后端 REST 输出开始按既有契约返回 `ApiResponse<T>` 和 camelCase 字段

### 下一步
- 进入 M1_2：WebSocket + MockAdapter 流式闭环
- 将 REST 降级接口 的消息持久化逻辑复用到 WS `send_message`

### 给其他成员的提醒
- @小马：Agent 列表现在有 mock seed，可用作后续 Adapter/LLMProvider 联调入口
- @洋芋：Artifact API 目前只是基础查询壳，完整产物生成会在 M1_2/M4 继续补

## [2026-05-24] Codex - AI 模块化开发流程沉淀

### 完成内容
- 新增 `docs/AI_WORKFLOW.md`，明确 AgentHub 标准模块化开发流程
- 新增项目本地 skill `agenthub-module-development`
- 更新 `AGENTS.md`，将 plan/checklist/test/verify/DEVLOG 流程纳入 AI 编码规则

### 新增/修改文件
- `docs/AI_WORKFLOW.md` (新增)
- `.agents/skills/agenthub-module-development/SKILL.md` (新增)
- `.agents/skills/agenthub-module-development/agents/openai.yaml` (新增)
- `AGENTS.md` (修改)
- `DEVLOG.md` (修改)

### 接口变更
- 无契约变更，未修改 `packages/shared/types.ts` 或 `docs/API_SPEC.md`

### 下一步
- 后续模块任务先使用 `agenthub-module-development` 流程生成 plan/checklist，再进入实现

### 给其他成员的提醒
- @小马：做 Adapter/LLMProvider 前先按 `docs/AI_WORKFLOW.md` 建对应计划和 checklist
- @洋芋：做 Artifact/Preview 时同样按该流程推进，尤其注意 shared types/API_SPEC 同步

## [2026-05-24] Codex - M1_2 WebSocket + MockAdapter 流式闭环

### 完成内容
- 新增 M1_2 plan/checklist，明确 WS + MockAdapter 后端闭环范围
- WebSocket `send_message` 不再 echo，改为持久化消息并推送 Mock 流式事件
- MockAdapter 输出文本、代码产物和 team note，WS 转换为 `text_delta`、`artifact`、`team_activity`、`message_done`

### 新增/修改文件
- `docs/plans/M1_2_PLAN.md` (新增)
- `docs/plans/M1_2_CHECKLIST.md` (新增)
- `backend/tests/test_m1_2_websocket.py` (新增)
- `backend/app/ws/handlers.py` (修改)
- `backend/app/adapters/mock.py` (修改)
- `backend/app/api/serializers.py` (修改)
- `backend/app/api/artifacts.py` (修改)

### 接口变更
- 未修改 `packages/shared/types.ts` 或 `docs/API_SPEC.md`
- WS 下行消息按既有 `WSServerMessage` 契约实现

### 下一步
- 进入 M1_3：前端三栏工作台、stores、API client 和 WebSocket hook

### 给其他成员的提醒
- @小马：MockAdapter 事件结构可作为后续 LLMProviderAdapter 的最低兼容目标
- @洋芋：Artifact 现在会从 WS 产出基础 code 类型，后续 CodeCard/PreviewPanel 可直接消费

## [2026-05-24] Codex - M1_3 前端工作台基础壳

### 完成内容
- 新增 M1_3 plan/checklist，明确前端基础壳范围
- 实现统一 API client、Zustand stores、WebSocket client 和 `useWebSocket`
- 工作台页面接入三栏布局，能加载 Agent/Conversation 并显示 WS 状态

### 新增/修改文件
- `docs/plans/M1_3_PLAN.md` (新增)
- `docs/plans/M1_3_CHECKLIST.md` (新增)
- `frontend/src/services/api.ts` (修改)
- `frontend/src/services/websocket.ts` (修改)
- `frontend/src/hooks/useWebSocket.ts` (修改)
- `frontend/src/stores/` (修改)
- `frontend/src/pages/Workspace.tsx` (修改)
- `frontend/src/components/` (修改)
- `frontend/src/index.css` (修改)

### 接口变更
- 未修改 `packages/shared/types.ts` 或 `docs/API_SPEC.md`
- 前端 API client 开始消费既有 `ApiResponse<T>` 契约

### 下一步
- 进入 M1_4：消息输入、流式消息展示、CodeCard 和全链路联调

### 给其他成员的提醒
- @小马：前端现在依赖 `/api/v1/agents` 返回 camelCase 字段
- @洋芋：PreviewPanel 目前是基础占位，M4 可以在此基础上接 Artifact 预览

## [2026-05-24] Codex - M1_4 聊天流 + 代码卡片 + 全链路联调

### 完成内容
- 新增 M1_4 plan/checklist，明确聊天流、代码卡片和 Mock 联调范围
- 实现 MessageInput、MessageBubble、CodeCard，并让 Workspace 通过 WS 发送消息
- 前端可接收 `text_delta` 和 `artifact`，更新消息流与 PreviewPanel

### 新增/修改文件
- `docs/plans/M1_4_PLAN.md` (新增)
- `docs/plans/M1_4_CHECKLIST.md` (新增)
- `frontend/src/components/chat/MessageInput.tsx` (修改)
- `frontend/src/components/chat/MessageBubble.tsx` (修改)
- `frontend/src/components/chat/ChatArea.tsx` (修改)
- `frontend/src/components/cards/CodeCard.tsx` (修改)
- `frontend/src/components/preview/PreviewPanel.tsx` (修改)
- `frontend/src/pages/Workspace.tsx` (修改)
- `frontend/src/index.css` (修改)

### 接口变更
- 无契约变更

### 下一步
- 做 M1 最终验收：同时启动前后端并进行浏览器端 Mock 闭环检查

### 给其他成员的提醒
- @小马：后续真实 Adapter 只要推送同样 WS 事件，前端聊天流即可复用
- @洋芋：CodeCard 是基础版，M4 产物阶段可替换为 Monaco/高亮增强版

## [2026-05-24] Codex - M1 Mock-first 完整闭环验收

### 完成内容
- 新增 M1 验收 checklist
- 完成后端 pytest、前端 build 和浏览器端 Mock 闭环验证
- 清理本地验收产生的 `agenthub.db` 和 `frontend/dist`

### 新增/修改文件
- `docs/plans/M1_ACCEPTANCE_CHECKLIST.md` (新增)
- `DEVLOG.md` (修改)

### 接口变更
- 无契约变更

### 下一步
- 进入 M2：会话列表完整交互、新建对话弹窗、@ 提及交互和 Orchestrator 基础框架

### 给其他成员的提醒
- @小马：M1 的 Mock WS 事件已经可作为真实 Adapter 输出契约参考
- @洋芋：M1 的 CodeCard/PreviewPanel 是基础版，占位清晰，后续可专注增强产物体验
## [2026-05-25] Codex - M1 稳定性优化与审查修复

### 完成内容
- 新增 M1 优化 plan/checklist，并按审查发现逐项修复。
- 后端补齐历史消息 artifacts/agentName、统一 422 错误格式、workDir/type/content 校验和 WS 异常清理。
- WebSocket 新增 `user_message` 下行事件，前端可用 `clientMessageId` 对齐乐观消息与服务端真实消息。
- 前端修复 stale socket 状态竞态、历史 artifact hydrate、发送失败反馈和关键中文文案。
- 通过 npm overrides 升级 transitive `dompurify`，清空 moderate audit 风险。

### 新增/修改文件
- `docs/plans/M1_OPTIMIZATION_PLAN.md` (新增)
- `docs/plans/M1_OPTIMIZATION_CHECKLIST.md` (新增)
- `docs/M1_OPTIMIZATION_SUMMARY.md` (新增)
- `backend/tests/test_m1_1_api.py` (修改)
- `backend/tests/test_m1_2_websocket.py` (修改)
- `backend/app/api/serializers.py` (修改)
- `backend/app/api/messages.py` (修改)
- `backend/app/api/responses.py` (修改)
- `backend/app/main.py` (修改)
- `backend/app/schemas/conversation.py` (修改)
- `backend/app/schemas/message.py` (修改)
- `backend/app/ws/handlers.py` (修改)
- `backend/app/ws/manager.py` (修改)
- `backend/app/adapters/mock.py` (修改)
- `frontend/src/services/websocket.ts` (修改)
- `frontend/src/hooks/useWebSocket.ts` (修改)
- `frontend/src/stores/messageStore.ts` (修改)
- `frontend/src/stores/artifactStore.ts` (修改)
- `frontend/src/pages/Workspace.tsx` (修改)
- `frontend/src/components/chat/MessageBubble.tsx` (修改)
- `frontend/src/components/preview/PreviewPanel.tsx` (修改)
- `frontend/package.json` / `frontend/package-lock.json` (修改)
- `packages/shared/types.ts` / `docs/API_SPEC.md` (修改)

### 接口变化
- WS 下行新增 `user_message`：服务端持久化用户消息后返回真实 message，并可携带 `clientMessageId`。
- `GET /conversations/{id}/messages` 的 agent 消息会带回已持久化 artifacts 和 `agentName`。
- FastAPI 422 validation error 统一为 `ApiResponse` 错误格式。

### 验证
- `cd backend && pytest -q` -> 8 项通过
- `cd frontend && npm run build` -> 通过
- `cd frontend && npm audit --audit-level=moderate` -> found 0 vulnerabilities

### 下一步
- 若继续 M2，优先基于当前 `user_message`/artifact hydrate 机制完善会话列表、新建会话弹窗和 @mention 交互。

### 给其他成员的提醒
- @小马：真实 Adapter 接入前请继续沿用 MockAdapter 的 WS 事件契约，尤其是 artifacts 与 `message_done` 的顺序。
- @洋芋：前端历史恢复已经可取回 CodeCard/PreviewPanel，后续 UI 增强可直接消费 message artifacts。
## [2026-05-25] Codex - M2 聊天核心

### 完成内容
- 新增 M2 总计划、M2_1-M2_6 子计划和 checklist。
- Conversation list 支持搜索最近消息、展示 lastMessage、参与者、会话类型和删除。
- 新增新建会话弹窗，支持单聊/群聊 Agent 选择和 workDir 输入。
- 实现 @ 提及 浮层选择，发送时解析 提及，单聊支持默认参与者降级逻辑。
- 新增规则版 OrchestratorService：按 mention/participant 顺序生成 sequential DispatchPlan。
- WebSocket 主流程接入 Orchestrator，推送 dispatching/executing/summarizing 状态，并为每个选中 Agent 运行 MockAdapter。
- 前端接入 agent_thinking/orchestrator_status/error runtime 状态，消息气泡展示头像、角色、时间和流式状态。

### 新增/修改文件
- `docs/plans/M2_TOTAL_PLAN.md` / `docs/plans/M2_TOTAL_CHECKLIST.md` (新增)
- `docs/plans/M2_1_PLAN.md` ... `docs/plans/M2_6_CHECKLIST.md` (新增)
- `backend/tests/test_m2_chat_core.py` (新增)
- `backend/app/services/orchestrator.py` (修改)
- `backend/app/ws/handlers.py` (修改)
- `backend/app/api/conversations.py` (修改)
- `frontend/src/services/api.ts` / `frontend/src/services/websocket.ts` (修改)
- `frontend/src/hooks/useWebSocket.ts` (修改)
- `frontend/src/stores/uiStore.ts` (修改)
- `frontend/src/pages/Workspace.tsx` (修改)
- `frontend/src/components/chat/*` (修改/新增)
- `frontend/src/index.css` (修改)

### 接口变化
- 无新增公开契约；复用现有 REST 和 WS 类型。
- `GET /conversations` 现在会返回可选 `lastMessage`，并允许 `search` 命中最近消息内容。
- WS 现在会在 Mock 执行前后推送 `orchestrator_status`。

### 验证
- `cd backend && pytest -q` -> 11 项通过
- `cd frontend && npm run build` -> 通过

### 下一步
- M3 可在当前 OrchestratorService 上加入 LLM 决策、上下文工程、TeamBoard/ProjectState 更新。

### 给其他成员的提醒
- @小马：真实 Adapter 接入时继续沿用 M2 的 WS 事件顺序；M2 仍只依赖 MockAdapter。
- @洋芋：消息流和 artifact store 已能消费多 Agent 产物，M4 可直接增强 CodeCard/PreviewPanel。

## [2026-05-26] Codex - M2 审查修复

### 完成内容
- 按 `docs/M2_REVIEW_REPORT.md` 修复 M2 审查发现：限制 WebSocket 提及只能调度会话参与 Agent，禁止空参与者会话，Adapter 失败时将任务标记为失败。
- 前端修复 mention 过匹配、运行时错误 粘滞、失败后 thinking 状态清理，以及会话列表 lastMessage/排序实时更新。
- 对齐 REST message fallback 文档：M2 仅持久化用户消息，不触发 Orchestrator。
- 清理 WebSocket 死 helper，并修复前端 lint 失败项。

### 新增/修改文件
- `backend/tests/test_m2_chat_core.py` (修改)
- `backend/app/api/conversations.py` (修改)
- `backend/app/schemas/conversation.py` (修改)
- `backend/app/ws/handlers.py` (修改)
- `frontend/src/services/api.ts` / `frontend/src/hooks/useWebSocket.ts` (修改)
- `frontend/src/stores/conversationStore.ts` / `frontend/src/stores/messageStore.ts` / `frontend/src/stores/uiStore.ts` (修改)
- `frontend/src/pages/Workspace.tsx` / `frontend/src/components/chat/ChatArea.tsx` (修改)
- `frontend/src/utils/diff.ts` (修改)
- `docs/API_SPEC.md` / `docs/plans/M2_TOTAL_PLAN.md` / `docs/plans/M2_TOTAL_CHECKLIST.md` (修改)

### 接口变化
- 无新增 WS 事件类型；失败任务继续通过现有 `error` 与 `orchestrator_status` 表达。
- `POST /conversations` / `PATCH /conversations/{id}` 现在拒绝空 `participantIds`。
- `GET /conversations` 的 `lastMessage` 语义保持不变。

### 验证
- `cd backend && pytest -q` -> 14 项通过
- `cd frontend && npm run lint` -> 通过
- `cd frontend && npm run build` -> 通过

### 下一步
- 提交并创建 M2 PR，等待 GitHub merge。

### 给其他成员的提醒
- @小马：真实 Adapter 异常时请沿用 `error` + 任务失败状态的终止语义。
- @洋芋：M4 预览增强可继续消费当前多 Agent message/artifact store。
## [2026-05-26] Codex - M2 审查报告

### 完成内容
- 将 M2 严格代码审查结果沉淀为独立交接文档，供负责开发的 Agent 按优先级优化。
- 文档覆盖 WebSocket 失败状态、会话 Agent 边界、空参与者降级逻辑、REST 降级接口 契约、@mention 解析、会话列表同步、运行时错误、lint 和死代码清理。

### 新增/修改文件
- `docs/M2_REVIEW_REPORT.md` (新增)
- `DEVLOG.md` (修改)

### 接口变化
- 无实现接口变化；文档指出 `POST /conversations/{id}/messages` 与 API_SPEC 存在语义不一致，需要后续修正实现或文档。

### 验证
- 本次为审查文档沉淀，未修改业务实现；沿用审查时的验证快照：`pytest -q` 11 项通过，`frontend npm run build` 通过，`frontend npm run lint` 失败。

### 下一步
- 开发 Agent 优先处理 `docs/M2_REVIEW_REPORT.md` 中 P1 项，再补充对应回归测试。
## [2026-05-28] Codex - M2 UI Interactions

### 完成内容
- 新增 `M2_UI_INTERACTIONS` plan/checklist，明确本轮只实现无需后端支持的前端交互。
- 新增 `docs/TECH_DEBT.md`，记录 UI polish 后暂未实现按钮的预期功能、当前状态和建议阶段。
- 聊天顶部将参与数量和更新时间改为只读状态文本，避免无交互图标误导；更新时间由前端本地时钟刷新。
- `+ 添加代理` chip 保留为未来自定义 Agent/参与者管理入口，并通过 title 标注后续扩展方向。
- 右侧预览区桌面/平板/手机图标改为真实按钮，可切换预览 viewport。
- 右侧预览区 `- / +` 缩放按钮接入前端状态，支持 75% / 100% / 125%。

### 新增/修改文件
- `docs/plans/M2_UI_INTERACTIONS_PLAN.md` (新增)
- `docs/plans/M2_UI_INTERACTIONS_CHECKLIST.md` (新增)
- `docs/TECH_DEBT.md` (新增)
- `frontend/src/components/chat/ChatArea.tsx` (修改)
- `frontend/src/components/preview/PreviewPanel.tsx` (修改)
- `frontend/src/index.css` (修改)
- `DEVLOG.md` (修改)

### 接口变化
- 无后端接口变化。
- 无 shared types 变化。
- 无新增依赖。

### 验证
- `cd frontend && npm run lint` -> 通过
- `cd frontend && npm run build` -> 通过
- 浏览器烟测：聊天顶部显示“X 个代理参与”和更新时间；桌面/平板/手机预览按钮均能切换 active；缩放按钮能更新到 `125%`；AgentHub 页面 console 无 error。

### 下一步
- 优先从 `docs/TECH_DEBT.md` 中挑选低成本高收益项继续补齐，例如 `@ 代理` 快捷按钮打开 mention selector、产物卡“预览”自动切换右侧预览 Tab、编辑会话标题。

## [2026-05-28] Codex - M2 UI Polish

### 完成内容
- 新增 `M2_UI_POLISH` plan/checklist，明确本轮只做前端视觉优化，不修改后端、共享类型或 API 契约。
- 按参考图重塑三栏工作台：左侧 AgentHub 品牌区、橙色新建按钮、常用代理卡片、对话列表卡片和底部操作。
- 优化聊天区：顶部会话标题、参与 Agent chip、派生协作状态、消息卡片、协作状态卡和输入工具条。
- 优化产物卡片：从代码块展示改为文件产物行，包含图标、文件名、类型/大小、生成状态和预览按钮。
- 重写右侧 PreviewPanel，支持 `产出物 | 预览 | 变更` 三 Tab；HTML artifact 通过前端 `iframe srcDoc` 预览，暂不依赖后端 Preview Service。

### 新增/修改文件
- `docs/plans/M2_UI_POLISH_PLAN.md` (新增)
- `docs/plans/M2_UI_POLISH_CHECKLIST.md` (新增)
- `frontend/src/components/chat/ConversationList.tsx` (修改)
- `frontend/src/components/chat/ChatArea.tsx` (修改)
- `frontend/src/components/chat/MessageBubble.tsx` (修改)
- `frontend/src/components/chat/MessageInput.tsx` (修改)
- `frontend/src/components/cards/CodeCard.tsx` (修改)
- `frontend/src/components/preview/PreviewPanel.tsx` (修改)
- `frontend/src/index.css` (修改)
- `DEVLOG.md` (修改)

### 接口变化
- 无后端接口变化。
- 无 `packages/shared/types.ts` 变化。
- 顶部状态只从现有前端数据和 WebSocket runtime 派生，不展示真实在线人数或平台健康状态。

### 验证
- `cd frontend && npm run lint` -> 通过
- `cd frontend && npm run build` -> 通过
- 浏览器烟测：`http://localhost:5173/workspace` 可打开；有产物会话中 `产出物` 能列出 `index.html`，`预览` 能显示 preview shell，`变更` 能显示空态；发送 `@代码工匠 视觉优化后再生成一次` 后 Mock 回复和产物正常出现，浏览器 console 无 error。

### 下一步
- 继续在 M2 UI polish 范围内补细节时，可优先处理空状态文案、会话时间显示真实化、Preview 面板全屏/缩放交互。
- 进入 M3 前仍不建议加入真实 presence 文案，除非后端新增 `presence_update` 或 Agent health 状态。

## [2026-05-28] Codex - M3 DeepSeek LLM 后端文档

### 完成内容
- 新增 `M3_DEEPSEEK_LLM_BACKEND` plan/checklist，明确本轮只调整文档策略，不改运行代码、不写入 `.env`。
- 将 PRD、技术设计、任务拆解、API 示例中的默认 LLM 后端从火山方舟调整为私人 DeepSeek API。
- 明确 DeepSeek 是 Orchestrator / LLMProvider 的模型后端，不计入“至少两个 Agent 平台”；平台接入仍由 OpenCode + Codex 满足。
- 记录 DeepSeek `deepseek-v4-flash` 官方价格页在 2026-05-28 查询到的预算估算，并加入赛前复核提醒。
- 补充 API Key 安全与预算控制策略：仅后端使用、Mock-first、限制 max_tokens/超时/重试、记录 token usage 与估算费用。

### 新增/修改文件
- `docs/plans/M3_DEEPSEEK_LLM_BACKEND_PLAN.md` (新增)
- `docs/plans/M3_DEEPSEEK_LLM_BACKEND_CHECKLIST.md` (新增)
- `docs/PRD.md` (修改)
- `docs/TECH_DESIGN.md` (修改)
- `docs/TASK_BREAKDOWN.md` (修改)
- `docs/API_SPEC.md` (修改)
- `docs/plans/M1_TOTAL_PLAN.md` (修改)
- `docs/plans/M2_TOTAL_PLAN.md` (修改)
- `DEVLOG.md` (修改)

### 接口变化
- 无后端接口变化。
- 无 `packages/shared/types.ts` 变化。
- 文档中的 `llm` provider 示例配置更新为 `https://api.deepseek.com` + `deepseek-v4-flash`。

### 验证
- 文档 grep：`docs/PRD.md`、`docs/TECH_DESIGN.md`、`docs/TASK_BREAKDOWN.md`、`docs/API_SPEC.md` 中已无未来默认 LLM 后端指向火山方舟的描述。
- 未运行代码测试：本轮仅修改文档。

### 下一步
- M3 实现时先补 `LLMProviderAdapter` 的 DeepSeek OpenAI 兼容客户端，再把 Orchestrator LLM 决策接到同一个 client。
- 保留 MockAdapter 作为开发、CI、答辩兜底路径。

## [2026-05-29] Codex - M2 DeepSeek Adapter 接入完成

### 完成内容
- 新建 `codex/m2-deepseek-completion` 开发分支。
- 新增 `M2_DEEPSEEK_ADAPTER` plan/checklist，明确本轮只补小马 M2 后端范围：DeepSeek LLMProvider、AgentManager、API-spec PUT 兼容。
- 实现 `LLMProviderAdapter`：读取 仅后端使用的 `DEEPSEEK_API_KEY`/base URL/model 配置，调用 DeepSeek OpenAI 兼容的流式聊天补全接口，解析 SSE `text_delta`，缺 key 时输出 `error` + `done`，并将 围栏代码块 转为 `file_created` 事件。
- 实现 `AgentManagerService` Adapter 工厂、缓存和健康检查，支持 `mock | llm | opencode | codex`。
- WebSocket dispatch 改为按 Agent `platform_id` 选择 adapter；M2 内置 Agent 仍保持 Mock-backed。
- Agent 更新接口新增 `PUT /api/v1/agents/{id}`，与 API_SPEC 对齐，同时保留 `PATCH`。
- 兼容 Windows 风格 `D:/.../workspaces/...` workDir 测试输入，并保持 `../outside` 路径校验。

### 新增/修改文件
- `docs/plans/M2_DEEPSEEK_ADAPTER_PLAN.md` (新增)
- `docs/plans/M2_DEEPSEEK_ADAPTER_CHECKLIST.md` (新增)
- `backend/tests/test_m2_deepseek_adapter.py` (新增)
- `backend/app/adapters/llm_provider.py` (修改)
- `backend/app/services/agent_manager.py` (修改)
- `backend/app/ws/handlers.py` (修改)
- `backend/app/api/agents.py` (修改)
- `backend/app/config.py` (修改)
- `backend/app/services/seed.py` (修改)
- `backend/app/schemas/conversation.py` (修改)
- `backend/requirements.txt` (修改)
- `frontend/package-lock.json` (修改：同步 npm lockfile 以恢复 `npm ci`/build)

### 接口变化
- 新增 `PUT /api/v1/agents/{id}` 实现，匹配既有 `docs/API_SPEC.md`；`PATCH` 保持可用。
- 无 `packages/shared/types.ts` 变化。
- DeepSeek API Key 只从运行时环境变量读取，未写入 `.env` 或仓库。

### 验证
- `cd backend && ../.venv/bin/python -m pytest -q tests/test_m2_deepseek_adapter.py` -> 4 项通过
- `cd backend && ../.venv/bin/python -m pytest -q` -> 19 项通过
- `cd frontend && npm run build` -> 通过，保留 Vite chunk 大小警告

### 下一步
- 若要真实联调 DeepSeek，请在本机后端运行环境设置 `DEEPSEEK_API_KEY`，不要提交到仓库。
- M3 可继续在同一个 AgentManager 基础上接 OpenCode/Codex CLI，并保留 CLI -> LLM -> Mock 降级策略。

## [2026-05-31] Codex - M4 Artifact 预览系统

### 完成内容
- 当前工作已在 `codex-m4-artifact-preview-system` 分支上继续。
- 按 `agenthub-module-development` workflow 新增 `M4_ARTIFACT_PREVIEW` plan/checklist，确认洋芋当前阶段负责 M4 产物与预览系统。
- 新增 M4 后端测试用例，覆盖 Mock 生成网页产物、`/preview/{conversation_id}/index.html` 原始文件预览、FileWatcher 修改 diff。
- 实现 `FileWatcherService` 目录快照与 created/modified/deleted 变更检测，输出契约内 `DiffData`。
- 实现 `ArtifactService`：从 `file_created/file_modified` AgentEvent 生成 webpage/code/diff Artifact，写入 workspace 文件，并生成 preview URL。
- 新增 `/preview/{conversation_id}/{filepath}` 根路径预览路由，包含路径穿越保护、Content-Type、CSP 与 nosniff header。
- 新增 `GET /conversations/{conversation_id}/artifacts`，补齐 `GET /artifacts/{id}/versions` 简版查询。
- WebSocket artifact 生成改为走 ArtifactService；Mock HTML 现在会作为 `webpage` 产物推送。
- 前端替换 CodeCard/DiffCard/WebPreviewCard/PreviewPanel/CodeEditor/DiffViewer/IframePreview 占位，实现聊天流卡片、iframe 预览、Monaco 只读代码和 Diff 视图。
- Vite 开发服务器代理新增 `/preview` 到后端。

### 新增/修改文件
- `docs/plans/M4_ARTIFACT_PREVIEW_PLAN.md`
- `docs/plans/M4_ARTIFACT_PREVIEW_CHECKLIST.md`
- `backend/tests/test_m4_artifact_preview.py`
- `backend/tests/test_m1_2_websocket.py`
- `backend/app/services/artifact_service.py`
- `backend/app/services/file_watcher.py`
- `backend/app/services/preview_service.py`
- `backend/app/main.py`
- `backend/app/ws/handlers.py`
- `backend/app/api/conversations.py`
- `backend/app/api/artifacts.py`
- `frontend/src/components/cards/*`
- `frontend/src/components/preview/*`
- `frontend/src/components/chat/MessageBubble.tsx`
- `frontend/src/index.css`
- `frontend/vite.config.ts`

### 接口变化
- 无 `packages/shared/types.ts` 变化。
- 新增实现：`GET /preview/{conversation_id}/{filepath}` 原始静态文件响应。
- 新增实现：`GET /api/v1/conversations/{conversation_id}/artifacts`。
- `MockAdapter` HTML 文件产物从 `code` 升级为更符合契约的 `webpage` artifact，并带可用 `previewUrl`（当 workDir 可写）。
- `GET /api/v1/conversations/{conversation_id}/artifacts` 的 `type` 重复查询参数显式使用 FastAPI `Query`，匹配 `?type=code&type=webpage`。

### 验证
- `git status --short --branch` -> 当前分支 `codex-m4-artifact-preview-system`
- `cd backend && python -m compileall app` -> 通过
- `cd backend && .\.venv\Scripts\python.exe -m pytest -q tests/test_m4_artifact_preview.py` -> 2 项通过
- `cd backend && .\.venv\Scripts\python.exe -m pytest -q` -> 23 项通过
- `cd frontend && npm run build` -> 通过
- 剩余警告：Starlette/httpx 弃用警告、pytest 缓存警告、Vite chunk 大小警告
- 修复验证中暴露的问题：M4 测试改用项目 `workspaces/` 目录，避免 schema 拒绝临时目录；移除前端未使用 `ZOOM_STEP`；相对 `workDir` 统一解析到项目根目录。

### 下一步
- M5 可在当前 DiffData 和 PreviewPanel 基础上继续做一键应用 Diff、版本历史切换、多文件预览增强。
- 后续可考虑拆分 Monaco/AntD 相关 chunk，消除 Vite 500 kB chunk 大小警告。

### 追加修复
- 修复聊天流产物卡片“打开”无明显反应的问题：`artifactStore` 现在保存完整 `activeArtifact`，卡片打开动作会携带 artifact 对象，PreviewPanel 即使遇到历史消息或 store 未同步列表也能展示对应产物。
- 验证：`cd frontend && npm run build` -> 通过，保留 Vite chunk 大小警告。
- 修复 Agent 更新接口忽略 `platformId` 的问题：`AgentUpdate` schema 现在接收 `platformId` alias，支持把内置 Agent 从 `mock` 切到 `llm`。
- 验证：`cd backend && .\.venv\Scripts\python.exe -m pytest -q tests/test_m2_chat_core.py tests/test_m4_artifact_preview.py` -> 10 项通过。
- 修复真实 LLM 长 HTML 回复没有闭合 围栏代码块 时不生成 artifact 的问题：LLMProvider 现在允许代码块延续到文本结尾，仍可提取 `file_created` 事件。
- 验证：`cd backend && .\.venv\Scripts\python.exe -m pytest -q tests/test_m2_deepseek_adapter.py tests/test_m2_chat_core.py tests/test_m4_artifact_preview.py` -> 15 项通过。
- 明确聊天卡片“打开”语义：它会在右侧 PreviewPanel 选中该 artifact 并切到对应 tab，不会新开浏览器窗口。为重复点击同一产物增加 `openRevision`，确保即使 active artifact 未变化，也会把右侧切回预览/代码/变更 tab。
- 验证：`cd frontend && npm run build` -> 通过，保留 Vite chunk 大小警告。
- 将产物卡片主操作文案从“打开”改为“在右侧查看”；网页产物额外提供外链图标按钮，用于新标签页打开 `previewUrl`。
- 验证：`cd frontend && npm run build` -> 通过，保留 Vite chunk 大小警告。
- 修复右侧网页预览无法交互的问题：主预览 iframe 的 sandbox 增加 `allow-scripts allow-forms allow-same-origin`，支持 AI 产物中的按钮事件和本地存储；聊天流缩略图仍保持不可交互。
- 验证：`cd frontend && npm run build` -> 通过，保留 Vite chunk 大小警告。
## [2026-05-30] Codex - M3 Orchestrator Planner 设计

### 完成内容
- 新增 M3 Orchestrator Planner v1.0 详细设计文档，沉淀已确认的 LLM-only 规划、规则校验和静态 DAG 批次推导方案。
- 明确简单并行约束：默认并发上限为 `3`，同批最多 `1` 个 `write`，每个 `read` 任务使用独立临时副本。
- 明确 Planner 的澄清问题、能力缺口推荐、非法计划重规划、风险确认、预算和可观测性策略。
- 将四层上下文、Team Board 和 Project State 详细设计保留为代码实现前必须完成的后续设计项。

### 新增/修改文件
- `docs/plans/M3_ORCHESTRATOR_PLANNER_DESIGN.md` (新增)
- `DEVLOG.md` (修改)

### 接口变化
- 无运行时代码变化。
- 无 `packages/shared/types.ts` 变化。
- 无 `docs/API_SPEC.md` 变化。
- 设计文档记录了 M3 实现阶段需要同步完成的契约变更。

### 验证
- 人工复核：设计文档包含已确认的 Planner 输入、输出协议、Prompt 规则、校验流程、批次推导、并行限制、预算和 WS 事件。
- 未运行代码测试：本轮仅新增设计文档和 DEVLOG 记录。

### 下一步
- 继续细化四层上下文的数据来源、预算、筛选、压缩和刷新规则。
- 在整体 M3 设计确认后，再统一更新共享类型和 API 契约并开始实现。

## [2026-05-31] Codex - M3 Orchestrator 协作设计

### 完成内容
- 新增 M3 Orchestrator 协作上下文与状态设计文档，覆盖 `3.8` 至 `3.11` 的已确认方案。
- 将原重型四层上下文收缩为 `PlannerContext + AgentHandoffEnvelope`，由 Codex/OpenCode CLI 自主探索受限工作目录。
- 确认 Team Board 使用单快照与原子 Team Notes 混合存储，并在批次屏障统一合并。
- 确认 Project State 使用 Python 扫描、Git Inspector 和 DeepSeek 增量摘要，摘要失败不阻塞执行。
- 确认 OrchestratorStatus 使用完整快照、单会话单活跃 Run、FIFO 消息队列、整 Run 取消和断线恢复策略。

### 新增/修改文件
- `docs/plans/M3_ORCHESTRATOR_COORDINATION_DESIGN.md` (新增)
- `DEVLOG.md` (修改)

### 接口变化
- 无运行时代码变化。
- 无 `packages/shared/types.ts` 变化。
- 无 `docs/API_SPEC.md` 变化。
- 设计文档记录了 M3 实现阶段需要同步完成的契约变更。

### 验证
- 人工复核：联合设计文档覆盖轻量上下文交接、快照并行、Team Notes 生命周期、Team Board 合并、Project State 刷新、完整状态快照、消息队列、失败取消和断线重连。
- 未运行代码测试：本轮仅新增设计文档和 DEVLOG 记录。

### 下一步
- 进入 M3 总体实现计划与 checklist 编写。
- 在实施前同步更新共享类型与 API 契约。

## [2026-05-31] Codex - M3 总体实施计划

### 完成内容
- 新增 M3 总体实现计划和 checklist，将真实 Agent 接入、Orchestrator 增强与协作状态拆分为十一块可独立验收的实施模块。
- 明确小马 Adapter 主线与组长 Orchestrator 主线的并行关系、依赖图、测试边界和 Day 12 验收场景。
- 为每个模块记录目标文件、Test-first 要求、验收标准和后续子计划命名。

### 新增/修改文件
- `docs/plans/M3_TOTAL_PLAN.md` (新增)
- `docs/plans/M3_TOTAL_CHECKLIST.md` (新增)
- `DEVLOG.md` (修改)

### 接口变化
- 无运行时代码变化。
- 无 `packages/shared/types.ts` 变化。
- 无 `docs/API_SPEC.md` 变化。
- 总体计划要求从 `M3_0` 开始同步更新共享类型和 API 契约。

### 验证
- 人工复核：总体计划覆盖 `3.1 - 3.11`、DeepSeek 依赖基线、Mock-first 测试、前后端协作状态和全链路验收。
- 未运行代码测试：本轮仅新增计划、checklist 和 DEVLOG 记录。

### 下一步
- 从 `M3_0 契约冻结与测试骨架` 开始实施。
- 每个模块开始前创建对应子计划和 checklist，按 Test-first 流程推进。


## [2026-05-31] Codex - M3 Orchestrator 运行时实现

### 完成内容
- 实现 M3 契约、DeepSeek 客户端、LLMProvider、CLI Adapter、进程生命周期管理、Adapter 降级、持久化模型和 Alembic 迁移。
- 新增安全 workspace 扫描、Git 检查、轻量交接、隔离只读快照、Planner 校验、确定性调度、FIFO 运行时执行、取消和持久化重连恢复。
- 新增 Team Board 原子笔记、去重、问题解决、确定性合并、冲突时 `review_required` 降级、可选 DeepSeek patch 摘要和非阻塞警告。
- 新增 Project State 确定性事实、可选 DeepSeek 摘要、摘要失败警告、GET API、WebSocket 协作事件、澄清恢复、能力推荐确认和提权写入审批。
- 新增前端协作状态、过期序列拒绝、批次展示、输入卡片和审批卡片、Team Board 展示、Project State 展示和共享状态刷新处理。
- 新增 `docs/M3_API_CONTRACT.md`、`docs/plans/M3_IMPLEMENTATION_REPORT.md`、子计划/checklist 和 CLI 调研结论。

### 验证
- `cd backend && pytest -q`
- `cd frontend && npm run lint`
- `cd frontend && npm run build`
- 空 SQLite 数据库执行 `alembic upgrade head`
- Mock-first 浏览器群聊烟测：成功渲染两个 Agent 回复和产物卡片。
- 有意跳过 DeepSeek 真实健康检查。传入的 API Key 未持久化、未回显；fake transport 覆盖通过。
- OpenCode help 烟测通过。Codex 桌面可执行文件返回拒绝访问，按预期保持为降级场景。

## [2026-05-31] Codex - M3 严格审查优化 Checklist

### 完成内容
- 审查 M3 实现产物、API 契约、运行时代码路径、前端 WebSocket 状态处理和里程碑文档。
- 新增 `docs/plans/M3_OPTIMIZATION_CHECKLIST.md`，作为可直接交给 Agent 执行的整改文档，按优先级记录 P0、P1 和 P2 问题。
- 补充证据位置、必需修复项、验收标准、推荐执行顺序和验证步骤。
- 记录已复现的运行时缺口：取消操作会等待阻塞中的 Agent 工作、跨会话审批可能修改另一个暂停任务、Project State GET 在 workspace 未变化时仍会增加版本号。

### 新增/修改文件
- `docs/plans/M3_OPTIMIZATION_CHECKLIST.md`（新增）
- `DEVLOG.md`（修改）

### 接口变更
- 无运行时代码变更。
- 未修改 `packages/shared/types.ts`。
- 未修改 `docs/API_SPEC.md`。

### 验证
- 根据 M3 严格审查结果人工复核 checklist。
- 写入文档后运行 `git diff --check`。
- 未重新运行代码测试：本轮只新增审查文档和 DEVLOG 记录。

### 下一步
- 将 `docs/plans/M3_OPTIMIZATION_CHECKLIST.md` 交给开发 Agent。
- 在 M3 验收前修复 P0 项，再按文档顺序完成 P1 稳定性改进。

## [2026-05-31] Codex - M3 严格审查稳定性修复完成

### 完成内容
- 关闭 `docs/plans/M3_OPTIMIZATION_CHECKLIST.md` 中的全部 P0、P1 和 P2 项。
- 新增活跃 Agent 工作的 prompt 取消、逐任务 workspace 审计、写任务无实际修改时判定失败、有限快照、安全只读 Adapter 降级、全局 CLI 并发限制和弹性广播。
- 稳定 Planner 和 WebSocket 状态处理：`cannot_plan` 可恢复、澄清答案原子提交、暂停任务校验会话归属、过期前端快照无副作用、重连使用有限退避。
- 每批任务后刷新 Team Board 和 Project State，使 Project State 读取幂等，增强 Team Board 合并，并在重启后显式协调过期的持久化运行记录。
- 将 DeepSeek 处理改为增量 SSE 流式传输，使 Alembic 与应用配置一致，并延迟加载较重的前端路由和预览 UI。

### 接口变更
- 澄清响应会原子发送全部必填答案。
- Planner 返回 `cannot_plan` 时，输出失败快照和可恢复 WebSocket 错误，不再输出输入卡片。
- 后端重启后，无法恢复仅存在于内存中的执行状态时，持久化的未终止运行记录会协调为失败。
- 只有 workspace 审计记录到真实文件变化时，写任务才会完成；降级和审计警告仍对用户可见。

### 验证
- `cd backend && python -u -m pytest -q` -> `114 项通过`
- `cd frontend && npm test` -> `3 项通过`
- `cd frontend && npm run lint` -> 通过
- `cd frontend && npm run build` -> 通过，无 chunk 警告
- `git diff --check` -> 通过
- 临时 SQLite `alembic upgrade head` 烟测 -> 通过
- 定向 Mock-first、阻塞取消和重启协调烟测套件 -> `4 项通过`

## [2026-05-31] Codex - M3 主分支集成

### 完成内容
- PR `#3`（`codex/m2-deepseek-adapter-ready`）和 PR `#4`（`codex-m4-artifact-preview-system`）合并后，将 `codex/m3-main-integration` 快进到 `origin/main`。
- 解决 `DEVLOG.md`、`llm_provider.py`、`main.py`、`agent_manager.py` 和 `ws/handlers.py` 中共享入口的冲突。
- 保留可复用的 M3 `LLMClient` 流式传输、重试和健康检查路径，同时恢复 M2 fenced code 产物提取和 AsyncClient 测试注入兼容性。
- 保留 M3 队列、取消、交接、降级和共享状态刷新行为，同时通过 M4 `ArtifactService` 路由文件事件。
- 保留 M4 预览路由，并移除自动合并引入的重复 DeepSeek Settings 字段。
- 将 PreviewPanel 同步 effect 状态更新替换为基于 artifact ID 和打开版本派生的 Tab 选择；保留重复打开时重置 Tab 的行为，同时满足 React lint 规则。

### 验证
- 冲突相关后端套件 -> `35 项通过`
- `cd backend && python -u -m pytest -q` -> `122 项通过`
- `cd frontend && npm test` -> `3 项通过`
- `cd frontend && npm run lint` -> 通过
- `cd frontend && npm run build` -> 通过
- `git diff --check` -> 通过
- 临时 SQLite `alembic upgrade head` -> 通过

### 给其他成员的提醒
- 安全 stash `safety: m3 before origin-main integration` 会有意保留，直到集成后的 M3 工作完成提交。

## [2026-06-01] Codex - M3 Codex CLI 集成

### 完成内容
- 为剩余的小马 M3 Agent 接入缺口新增 `M3_CODEX_CLI_INTEGRATION` plan/checklist。
- 更新 `CodexAdapter`，使用当前本地 CLI 路径：
  `codex --ask-for-approval never exec --json --cd <workspace> --sandbox workspace-write --skip-git-repo-check <prompt>`。
- 将真实 Codex JSONL `item.completed` Agent 消息解析为 `text_delta`。
- 新增 workspace 执行前后快照，使 Codex 创建和修改的文本文件通过 ArtifactService 发出标准 `file_created` / `file_modified` 事件。
- 在 M3 schema 校验前，规范化真实 DeepSeek Planner 输出变体（`Ready`、`plan.tasks`、`readWriteAccess`、`description`、字符串 `acceptanceCriteria`）。
- 在应用总大小限制前对遍历顺序排序，使 M3 workspace 快照复制保持确定性。
- 刷新 `docs/CLI_AGENT_RESEARCH.md`，使用已通过的本地 CLI 烟测结果替换过期的 Codex 拒绝访问结论。

### 接口变更
- 无 shared types、REST 或 WebSocket 契约变更。
- 保留现有 `AgentAdapter` 和 `AgentEvent` 契约。

### 验证
- `cd backend && ../.venv/bin/python -m pytest -q tests/test_m3_cli_adapters.py` -> `4 项通过`
- `cd backend && ../.venv/bin/python -m pytest -q tests/test_m3_planner.py` -> `6 项通过`
- `cd backend && ../.venv/bin/python -m pytest -q tests/test_m3_planner.py tests/test_m3_cli_adapters.py` -> `10 项通过`
- `cd backend && ../.venv/bin/python -m pytest -q tests/test_m3_cli_adapters.py tests/test_m3_agent_manager.py tests/test_m3_websocket_runtime.py` -> `18 项通过`
- `cd backend && ../.venv/bin/python -m pytest -q tests/test_m3_workspace_snapshot.py tests/test_m3_cli_adapters.py tests/test_m3_agent_manager.py tests/test_m3_websocket_runtime.py` -> `21 项通过`
- `cd backend && ../.venv/bin/python -m pytest -q` -> `124 项通过`
- 真实本地 Codex Adapter 烟测：`CodexAdapter.run_task()` 创建 `adapter_smoke.txt`，依次发出 `text_delta`、`file_created` 和 `done`。
- 真实 DeepSeek Planner + Codex WebSocket 烟测：生成 `deepseek_codex_smoke.txt`，发出 `artifact`，最终状态为 `completed`。

### Next Steps
- For full product acceptance, run a browser/WebSocket conversation with a Codex-backed Agent selected in the database and confirm the chat artifact appears in the UI.
- OpenCode remains a one-shot minimal adapter; session support is still out of scope for this pass.

## [2026-06-01] Codex - M3 OpenCode DeepSeek Integration

### Completed
- Installed OpenCode through Homebrew after npm registry download stalls; verified `/opt/homebrew/bin/opencode` version `1.15.13` and `opencode run --help`.
- Updated `OpenCodeAdapter` to run the real one-shot CLI path:
  `opencode run --format json --model deepseek/deepseek-v4-flash --dir <workspace> --dangerously-skip-permissions <prompt>`.
- Added JSONL text extraction and before/after workspace snapshots so OpenCode-created and OpenCode-modified text files emit standard `file_created` / `file_modified` events.
- Recorded DeepSeek provider/model findings from OpenCode docs and Models.dev in `docs/CLI_AGENT_RESEARCH.md`.

### Added/Modified Files
- `backend/app/adapters/opencode.py` (modified)
- `backend/app/config.py` (modified)
- `backend/tests/test_m3_cli_adapters.py` (modified)
- `docs/CLI_AGENT_RESEARCH.md` (modified)
- `docs/plans/M3_2_CLI_ADAPTERS_CHECKLIST.md` (modified)
- `DEVLOG.md` (modified)

### Interface Changes
- No shared type, REST, or WebSocket contract changes.
- Added backend-only `OPENCODE_MODEL`, defaulting to `deepseek/deepseek-v4-flash`.

### Verification
- `opencode --version` -> `1.15.13`
- `opencode run --help` -> confirmed `--format`, `--model`, `--dir`, and `--dangerously-skip-permissions`.
- `/tmp/agenthub-test-venv311/bin/python -m pytest backend/tests/test_m3_cli_adapters.py backend/tests/test_m3_process_pool.py backend/tests/test_m3_agent_manager.py` -> `15 passed`
- `git diff --check` -> passed

### Next Steps
- Configure `DEEPSEEK_API_KEY` in the runtime environment before a real OpenCode task smoke; no `.env` secrets were edited.
- Session reuse remains out of scope; M3 uses one-shot `opencode run`.

### 下一步
- 完整产品验收时，在数据库中选中 Codex 支持的 Agent，运行一次浏览器/WebSocket 会话，确认聊天产物出现在 UI 中。
- OpenCode 仍为一次性最小 Adapter；session 支持仍不在本轮范围内。

## [2026-06-01] Codex - 隔离 Codex CLI DeepSeek 桥接

### 完成内容
- 复现 Windows 启动失败：`CODEX_BINARY_PATH=codex` 解析到 Microsoft Store 包资源二进制文件，其 ACL 要求 Codex Desktop 应用身份，FastAPI 后端子进程会被拒绝启动。
- 新增 Windows CLI 解析逻辑：优先使用 `%LOCALAPPDATA%\OpenAI\Codex\bin` 下可运行的 Codex Desktop 缓存，再回退到 PATH。
- 确认当前 Codex CLI 版本拒绝自定义 Provider 使用 `wire_api = "chat"`，要求使用 Responses 传输格式。
- 新增仅绑定本地回环地址、逐任务启动的 Responses 转 Chat 桥接服务，将 Codex 请求转发到后端配置的 DeepSeek 聊天补全 API。
- 新增逐次随机 桥接令牌、临时 `CODEX_HOME` 配置和子进程环境隔离，使 AgentHub 不会读取或修改活跃的 Codex Desktop 配置。
- 扩展 `ProcessPool`，支持显式注入子进程环境变量。
- 更新 `ProcessPool`：以主进程返回码作为权威状态，在有限时间内排空继承的 Windows 管道句柄，避免 Codex shell tool 执行后的假超时。
- 验证 `workspace-write` 会在 `windows sandbox: spawn setup refresh` 期间失败，且 `unelevated` 变通方案 无法写入任务 workspace 后，新增 Windows Codex `danger-full-access` 本机直接执行。非 Windows Codex 任务仍使用 `workspace-write`。
- 更新 `.env.example`、M3 plan/checklist 和 CLI 调研记录。

### 接口变更
- 无 shared types、REST 或 WebSocket 契约变更。
- `ProcessPool.run()` 接受可选的子进程 `env`。
- `CodexAdapter` 健康检查现在要求后端可用的 `DEEPSEEK_API_KEY`，其余情况下仍保留现有 `llm` / `mock` 降级链路。

### 验证
- RED：实现前调用 `ProcessPool.run(..., env=...)` 会因未预期的关键字参数失败。
- RED：实现前无法导入桥接服务和 Windows 解析器。
- `cd backend && python -m pytest tests/test_m3_process_pool.py tests/test_m3_deepseek_responses_bridge.py tests/test_m3_cli_adapters.py tests/test_m3_codex_cli_smoke.py -q` -> `18 项通过`
- `cd backend && python -m pytest -q` -> `137 项通过`
- `git diff --check` -> 通过
- 真实缓存 Codex CLI 伪上游烟测：CLI 从 `%LOCALAPPDATA%\OpenAI\Codex\bin` 解析，调用本地回环桥接服务；桥接服务发出 DeepSeek 聊天补全请求，AgentHub 依次收到 `text_delta: OK` 和 `done`。
- 真实 DeepSeek 文本烟测：隔离缓存 Codex CLI 健康检查返回 `True`，并返回 `LIVE_CODEX_DEEPSEEK_OK`。
- 真实 DeepSeek 文件烟测：隔离缓存 Codex CLI 创建 `live_codex_deepseek_smoke.txt`，内容为 `LIVE_FILE_OK\n`；AgentHub 依次发出 `text_delta`、`file_created` 和 `done`。

### 执行说明
- Windows CLI 任务有意使用 `danger-full-access` 直接在本机运行，因为上游 Windows sandbox 辅助程序 无法在此主机初始化。

## [2026-06-01] Codex - CLI 排障与跨平台指南

### 完成内容
- 新增 `docs/CODEX_CLI_CROSS_PLATFORM_GUIDE.md`，记录真实 Codex CLI 集成故障、根因、解决方案、验证阶梯和 Windows/macOS 协作矩阵。
- 记录不同平台在二进制文件发现、sandbox 行为、shell 语义、路径分隔符、绝对 workspace 路径、换行符、文件名大小写、临时文件锁和可执行文件后缀方面的差异。
- 在 `docs/CLI_AGENT_RESEARCH.md` 中新增团队指南入口。

### 接口变更
- 仅修改文档。无运行时、shared types、REST 或 WebSocket 变更。

### 验证
- `git diff --check` -> 通过。

## [2026-06-01] Codex - OpenCode 聊天摘要修复

### 完成内容
- 修复 OpenCode JSONL 输出兜底逻辑，避免未知 raw JSON 事件整段进入前端聊天框。
- 在 OpenCode 无明确 assistant 文本时生成简短执行摘要，包含查看文件、修改文件、命令执行等工作过程提示。
- 文件新增/修改内容继续通过 `file_created` / `file_modified` 产物事件展示，不混入聊天文本。

### 新增/修改文件
- `backend/app/adapters/opencode.py` (修改)
- `backend/tests/test_m3_cli_adapters.py` (修改)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST 或 WebSocket 契约变更。

### 验证
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q` -> `11 passed`
- `cd backend && ../.venv/bin/python -m pytest -q` -> `141 passed`
- Adapter fake raw JSONL 烟测：聊天输出为简短中文摘要，raw `unknown.raw` / `sessionID` 未进入文本，文件变更仍发出 `file_created`。

## [2026-06-01] Codex - 内置 Agent 默认切换到 OpenCode

### 完成内容
- 将 `代码工匠`、`审查大师`、`文档专家` 的后端 seed 默认 `platform_id` 全部改为 `opencode`。
- `seed_builtin_data()` 现在会把已有数据库中的这三个内置 Agent 规范化到 `opencode`，避免旧本地库继续停留在 `mock`。
- 调整 Mock 相关 WebSocket 测试，显式创建测试用 Mock Agent，不再依赖内置 Agent 默认是 Mock。
- 更新 Agent API 示例和 M3 计划/checklist。

### 新增/修改文件
- `backend/app/services/seed.py` (修改)
- `backend/tests/conftest.py` (修改)
- `backend/tests/test_m1_1_api.py` (修改)
- `backend/tests/test_m1_2_websocket.py` (修改)
- `backend/tests/test_m2_chat_core.py` (修改)
- `backend/tests/test_m3_e2e.py` (修改)
- `backend/tests/test_m3_websocket_interactions.py` (修改)
- `backend/tests/test_m3_websocket_runtime.py` (修改)
- `backend/tests/test_m4_artifact_preview.py` (修改)
- `docs/API_SPEC.md` (修改)
- `docs/plans/M3_BUILTIN_AGENT_OPENCODE_PLAN.md` (新增)
- `docs/plans/M3_BUILTIN_AGENT_OPENCODE_CHECKLIST.md` (新增)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST 或 WebSocket 结构变更。
- `GET /api/v1/agents` 中三个内置 Agent 的 `platformId` 默认值变为 `opencode`。

### 验证
- RED：新增 `test_builtin_agents_are_backed_by_opencode` 后，旧 seed 返回 `mock`，测试失败。
- `cd backend && ../.venv/bin/python -m pytest tests/test_m1_1_api.py::test_builtin_agents_are_backed_by_opencode -q` -> `1 passed`
- `cd backend && ../.venv/bin/python -m pytest tests/test_m1_1_api.py tests/test_m1_2_websocket.py tests/test_m2_chat_core.py tests/test_m3_websocket_runtime.py tests/test_m3_websocket_interactions.py tests/test_m3_e2e.py tests/test_m4_artifact_preview.py -q` -> `37 passed`
- `cd backend && ../.venv/bin/python -m pytest -q` -> `142 passed`
- 本地 `backend/agenthub.db` 查询确认三位内置 Agent 均为 `opencode`。

## [2026-06-01] Codex - OpenCode 群聊摘要与预览产物修复

### 完成内容
- 修复 OpenCode JSON 输出解析：对象型 `message`、工具 payload、`sessionID` 等 raw 结构不再直接进入聊天 `text_delta`。
- 保留简短中文执行摘要和工作过程提示；完整文件内容继续只通过 artifact 卡片展示。
- 对写入型“小程序/页面/预览”等任务追加 AgentHub 预览约束，明确要求创建或更新 `index.html`。
- 如果 OpenCode 第一轮只写了 README/文档、没有任何 HTML 预览入口，会自动追加一次聚焦修复执行，要求补齐 `index.html`。
- 新增群聊 WebSocket 回归，确认 opencode 群聊任务能广播 `webpage` artifact 且带 `/preview/{conversationId}/index.html`。

### 新增/修改文件
- `backend/app/adapters/opencode.py` (修改)
- `backend/tests/test_m3_cli_adapters.py` (修改)
- `backend/tests/test_m3_websocket_runtime.py` (修改)
- `docs/plans/M3_OPENCODE_GROUP_PREVIEW_FIX_PLAN.md` (新增)
- `docs/plans/M3_OPENCODE_GROUP_PREVIEW_FIX_CHECKLIST.md` (新增)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST 或 WebSocket 结构变更。
- OpenCode adapter 行为变更：聊天流更保守，预览任务会要求并补救生成 HTML 入口。

### 验证
- RED：对象型 OpenCode `message` 会把 `sessionID` / dict raw 串进聊天；修复后通过。
- RED：小程序/预览任务 prompt 未要求 `index.html`；修复后通过。
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q` -> `14 passed`
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py tests/test_m3_websocket_runtime.py tests/test_m4_artifact_preview.py -q` -> `27 passed`
- `cd backend && ../.venv/bin/python -m pytest -q` -> `146 passed`

## [2026-06-02] Codex - OpenCode 工具读取内容泄漏修复

### 完成内容
- 查看最近一次群聊 `d9fd2714-8eda-4248-83e3-846639a490ac`，确认 raw 来源是 OpenCode 工具读取文件时返回的行号 HTML、`</content>`、`metadata.preview` 和 `sessionID`，不是普通 assistant 回复。
- 扩展 OpenCode 文本提取逻辑：对疑似工具读取结果文本、带行号文件片段、HTML 预览内容和工具 metadata 只生成工作摘要，不推送到聊天 `text_delta`。
- 保留正常 assistant 文本、文件 artifact、diff artifact 和网页 preview。
- 清理最近一次群聊中已持久化的 3 条 raw agent 消息正文，保留原有 artifacts 和 `/preview/.../index.html`。

### 新增/修改文件
- `backend/app/adapters/opencode.py` (修改)
- `backend/tests/test_m3_cli_adapters.py` (修改)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST 或 WebSocket 结构变更。
- OpenCode adapter 对工具读取结果文本的过滤更严格。

### 验证
- RED：复现真实泄漏格式 `232: ... <script> ... </content>","metadata"... "sessionID"` 会进入聊天；修复后通过。
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q` -> `15 passed`
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py tests/test_m3_websocket_runtime.py tests/test_m4_artifact_preview.py -q` -> `28 passed`
- `cd backend && ../.venv/bin/python -m pytest -q` -> `147 passed`
- 最近群聊消息 raw 残留查询：`0`；artifact 查询仍保留 `webpage index.html` 及相关文档产物。
