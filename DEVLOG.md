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
- 增加 pytest 覆盖 Agent seed、会话 CRUD、消息 REST fallback 和错误响应格式

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
- 将 REST fallback 的消息持久化逻辑复用到 WS `send_message`

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
## [2026-05-25] Codex - M1 稳定性优化与 review 修复

### 完成内容
- 新增 M1 optimization plan/checklist，并按 review 发现逐项修复。
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
- `cd backend && pytest -q` -> 8 passed
- `cd frontend && npm run build` -> passed
- `cd frontend && npm audit --audit-level=moderate` -> found 0 vulnerabilities

### 下一步
- 若继续 M2，优先基于当前 `user_message`/artifact hydrate 机制完善会话列表、新建会话弹窗和 @mention 交互。

### 给其他成员的提醒
- @小马：真实 Adapter 接入前请继续沿用 MockAdapter 的 WS 事件契约，尤其是 artifacts 与 `message_done` 的顺序。
- @洋芋：前端历史恢复已经可取回 CodeCard/PreviewPanel，后续 UI 增强可直接消费 message artifacts。
## [2026-05-25] Codex - M2 Chat Core

### 完成内容
- 新增 M2 总计划、M2_1-M2_6 子计划和 checklist。
- Conversation list 支持搜索最近消息、展示 lastMessage、参与者、会话类型和删除。
- 新增新建会话弹窗，支持单聊/群聊 Agent 选择和 workDir 输入。
- 实现 @ mention 浮层选择，发送时解析 mentions，单聊支持默认参与者 fallback。
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
- `cd backend && pytest -q` -> 11 passed
- `cd frontend && npm run build` -> passed

### 下一步
- M3 可在当前 OrchestratorService 上加入 LLM 决策、上下文工程、TeamBoard/ProjectState 更新。

### 给其他成员的提醒
- @小马：真实 Adapter 接入时继续沿用 M2 的 WS 事件顺序；M2 仍只依赖 MockAdapter。
- @洋芋：消息流和 artifact store 已能消费多 Agent 产物，M4 可直接增强 CodeCard/PreviewPanel。

## [2026-05-26] Codex - M2 Review Fixes

### 完成内容
- 按 `docs/M2_REVIEW_REPORT.md` 修复 M2 review 发现：限制 WebSocket mention 只能调度会话参与 Agent，禁止空参与者会话，Adapter 失败时 task 标记为 failed。
- 前端修复 mention 过匹配、runtime error 粘滞、失败后 thinking 状态清理，以及会话列表 lastMessage/排序实时更新。
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
- `cd backend && pytest -q` -> 14 passed
- `cd frontend && npm run lint` -> passed
- `cd frontend && npm run build` -> passed

### 下一步
- 提交并创建 M2 PR，等待 GitHub merge。

### 给其他成员的提醒
- @小马：真实 Adapter 异常时请沿用 `error` + failed task status 的终止语义。
- @洋芋：M4 预览增强可继续消费当前多 Agent message/artifact store。
## [2026-05-26] Codex - M2 Review Report

### 完成内容
- 将 M2 严格代码审查结果沉淀为独立交接文档，供负责开发的 Agent 按优先级优化。
- 文档覆盖 WebSocket 失败状态、会话 Agent 边界、空参与者 fallback、REST fallback 契约、@mention 解析、会话列表同步、runtime error、lint 和死代码清理。

### 新增/修改文件
- `docs/M2_REVIEW_REPORT.md` (新增)
- `DEVLOG.md` (修改)

### 接口变化
- 无实现接口变化；文档指出 `POST /conversations/{id}/messages` 与 API_SPEC 存在语义不一致，需要后续修正实现或文档。

### 验证
- 本次为 review 文档沉淀，未修改业务实现；沿用 review 时的验证快照：`pytest -q` 11 passed，`frontend npm run build` passed，`frontend npm run lint` failed。

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
- `cd frontend && npm run lint` -> passed
- `cd frontend && npm run build` -> passed
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
- `cd frontend && npm run lint` -> passed
- `cd frontend && npm run build` -> passed
- 浏览器烟测：`http://localhost:5173/workspace` 可打开；有产物会话中 `产出物` 能列出 `index.html`，`预览` 能显示 preview shell，`变更` 能显示空态；发送 `@代码工匠 视觉优化后再生成一次` 后 Mock 回复和产物正常出现，浏览器 console 无 error。

### 下一步
- 继续在 M2 UI polish 范围内补细节时，可优先处理空状态文案、会话时间显示真实化、Preview 面板全屏/缩放交互。
- 进入 M3 前仍不建议加入真实 presence 文案，除非后端新增 `presence_update` 或 Agent health 状态。

## [2026-05-28] Codex - M3 DeepSeek LLM Backend Docs

### 完成内容
- 新增 `M3_DEEPSEEK_LLM_BACKEND` plan/checklist，明确本轮只调整文档策略，不改运行代码、不写入 `.env`。
- 将 PRD、技术设计、任务拆解、API 示例中的默认 LLM 后端从火山方舟调整为私人 DeepSeek API。
- 明确 DeepSeek 是 Orchestrator / LLMProvider 的模型后端，不计入“至少两个 Agent 平台”；平台接入仍由 OpenCode + Codex 满足。
- 记录 DeepSeek `deepseek-v4-flash` 官方价格页在 2026-05-28 查询到的预算估算，并加入赛前复核提醒。
- 补充 API Key 安全与预算控制策略：backend-only、Mock-first、限制 max_tokens/超时/重试、记录 token usage 与估算费用。

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
- M3 实现时先补 `LLMProviderAdapter` 的 DeepSeek OpenAI-compatible client，再把 Orchestrator LLM 决策接到同一个 client。
- 保留 MockAdapter 作为开发、CI、答辩兜底路径。
