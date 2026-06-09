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
- `cd frontend && npm audit --audit-level=moderate` -> 0 个漏洞

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

### 下一步
- 完整产品验收时，在数据库中选中 Codex 支持的 Agent，运行一次浏览器/WebSocket 会话，确认聊天产物出现在 UI 中。
- OpenCode 仍为一次性最小 Adapter；session 支持仍不在本轮范围内。

## [2026-06-01] Codex - M3 OpenCode DeepSeek 集成

### 完成内容
- npm registry 下载卡住后，改用 Homebrew 安装 OpenCode；已验证 `/opt/homebrew/bin/opencode` 版本为 `1.15.13`，并确认 `opencode run --help` 可用。
- 更新 `OpenCodeAdapter`，接入真实一次性 CLI 路径：
  `opencode run --format json --model deepseek/deepseek-v4-flash --dir <workspace> --dangerously-skip-permissions <prompt>`.
- 新增 JSONL 文本提取和执行前后 workspace 快照，使 OpenCode 创建/修改的文本文件能发出标准 `file_created` / `file_modified` 事件。
- 将 OpenCode 文档和 Models.dev 中关于 DeepSeek provider/model 的调研结果记录到 `docs/CLI_AGENT_RESEARCH.md`。

### 新增/修改文件
- `backend/app/adapters/opencode.py` (修改)
- `backend/app/config.py` (修改)
- `backend/tests/test_m3_cli_adapters.py` (修改)
- `docs/CLI_AGENT_RESEARCH.md` (修改)
- `docs/plans/M3_2_CLI_ADAPTERS_CHECKLIST.md` (修改)
- `DEVLOG.md` (修改)

### 接口变化
- 无 shared type、REST 或 WebSocket 契约变更。
- 新增仅后端使用的 `OPENCODE_MODEL`，默认值为 `deepseek/deepseek-v4-flash`。

### 验证
- `opencode --version` -> `1.15.13`
- `opencode run --help` -> 确认支持 `--format`、`--model`、`--dir` 和 `--dangerously-skip-permissions`。
- `/tmp/agenthub-test-venv311/bin/python -m pytest backend/tests/test_m3_cli_adapters.py backend/tests/test_m3_process_pool.py backend/tests/test_m3_agent_manager.py` -> `15 项通过`
- `git diff --check` -> 通过

### 下一步
- 真实 OpenCode 任务烟测前，请在运行环境配置 `DEEPSEEK_API_KEY`；本次未编辑任何 `.env` 凭据。
- session 复用仍不在本轮范围内；M3 使用一次性 `opencode run`。

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
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q` -> `11 项通过`
- `cd backend && ../.venv/bin/python -m pytest -q` -> `141 项通过`
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
- `cd backend && ../.venv/bin/python -m pytest tests/test_m1_1_api.py::test_builtin_agents_are_backed_by_opencode -q` -> `1 项通过`
- `cd backend && ../.venv/bin/python -m pytest tests/test_m1_1_api.py tests/test_m1_2_websocket.py tests/test_m2_chat_core.py tests/test_m3_websocket_runtime.py tests/test_m3_websocket_interactions.py tests/test_m3_e2e.py tests/test_m4_artifact_preview.py -q` -> `37 项通过`
- `cd backend && ../.venv/bin/python -m pytest -q` -> `142 项通过`
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
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q` -> `14 项通过`
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py tests/test_m3_websocket_runtime.py tests/test_m4_artifact_preview.py -q` -> `27 项通过`
- `cd backend && ../.venv/bin/python -m pytest -q` -> `146 项通过`

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
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q` -> `15 项通过`
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_cli_adapters.py tests/test_m3_websocket_runtime.py tests/test_m4_artifact_preview.py -q` -> `28 项通过`
- `cd backend && ../.venv/bin/python -m pytest -q` -> `147 项通过`
- 最近群聊消息 raw 残留查询：`0`；artifact 查询仍保留 `webpage index.html` 及相关文档产物。

## [2026-06-02] Codex - OpenCode assistant 代码块直出修复

### 当前进展判断
- 阅读 `AGENTS.md`、`docs/API_SPEC.md`、`packages/shared/types.ts`、`docs/TASK_BREAKDOWN.md` 和 M3 OpenCode 相关计划后确认：M1/M2/M3/M4 主链路已合入，当前问题属于 M3 OpenCode Adapter 输出清洗回归，不需要改 shared types、REST、WebSocket 或前端卡片契约。
- 查看 git 历史确认主线最近合入 PR #8，包含 OpenCode 默认内置 Agent、群聊摘要清洗、预览入口补救等改动；本次修复继续沿用该 adapter 层边界。

### 完成内容
- 新增 OpenCode assistant raw code 回归：模拟 OpenCode 已写入 `src/App.tsx`，但又把同一段 TSX fenced code 当作 assistant 文本返回。
- 扩展 OpenCode 文本提取：对 `message`、`message.part.*`、delta 聚合和 plain text 输出统一剥离 fenced code block。
- 若剥离后只剩源码或没有可读说明，则回落为简短中文执行摘要，提示代码产物已整理并通过 artifact 卡片展示。
- 保留 `file_created` / `file_modified` 事件不变，代码内容继续走产物卡片和预览链路。

### 新增/修改文件
- `backend/app/adapters/opencode.py` (修改)
- `backend/tests/test_m3_cli_adapters.py` (修改)
- `docs/plans/M3_OPENCODE_RAW_CODE_REPLY_FIX_PLAN.md` (新增)
- `docs/plans/M3_OPENCODE_RAW_CODE_REPLY_FIX_CHECKLIST.md` (新增)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST 或 WebSocket 结构变更。
- OpenCode adapter 行为变更：聊天 `text_delta` 更保守，fenced/raw source code 不再进入群聊回复正文。

### 验证
- RED：新增回归测试前，OpenCode assistant TSX fenced code 会作为 `text_delta` 进入消息 bubble。
- `cd backend && /private/tmp/agenthub-pytest-venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q` -> `16 项通过`
- `cd backend && /private/tmp/agenthub-pytest-venv/bin/python -m pytest tests/test_m3_cli_adapters.py tests/test_m3_websocket_runtime.py tests/test_m4_artifact_preview.py -q` -> `29 项通过`
- 沙箱内全量测试因 Codex smoke 绑定 `127.0.0.1` 被拒，非沙箱重跑通过：`cd backend && /private/tmp/agenthub-pytest-venv/bin/python -m pytest -q` -> `148 项通过`
- `git diff --check` -> 通过。

## [2026-06-02] Codex - OpenCode DeepSeek 环境注入

### 完成内容
- 修复 OpenCode 子进程无法直接读取 `backend/.env` 中 DeepSeek 配置的问题。
- `OpenCodeAdapter` 现在会为正常执行和 preview repair 执行显式传入子进程环境：
  - `DEEPSEEK_API_KEY`
  - `DEEPSEEK_BASE_URL`
  - `DEEPSEEK_MODEL`
- 保持 secret 后端内使用，不写入仓库、不记录、不返回给前端。

### 新增/修改文件
- `backend/app/adapters/opencode.py` (修改)
- `backend/tests/test_m3_cli_adapters.py` (修改)
- `docs/plans/M3_OPENCODE_DEEPSEEK_ENV_PLAN.md` (新增)
- `docs/plans/M3_OPENCODE_DEEPSEEK_ENV_CHECKLIST.md` (新增)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST 或 WebSocket 结构变更。
- OpenCode 子进程环境现在由后端显式注入 DeepSeek 配置。

### 验证
- RED：新增回归测试前，OpenCode process pool 收到的 `env` 为 `None`。
- `cd backend && .venv/bin/python -m pytest tests/test_m3_cli_adapters.py::test_opencode_adapter_passes_deepseek_env_to_child_process -q` -> `1 项通过`
- `cd backend && .venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q` -> `17 项通过`

## [2026-06-02] Codex - DeepSeek SOCKS 代理规划卡住修复

### 完成内容
- 排查前端停在 `Orchestrator: planning` 的原因：本机环境存在 `ALL_PROXY=socks5://127.0.0.1:7897`，但后端 `httpx` 未安装 SOCKS extra，DeepSeek Planner 初始化 HTTP client 时抛出 `socksio` 缺失异常。
- 将后端依赖从 `httpx>=0.25.0` 改为 `httpx[socks]>=0.25.0`，并在本地 `.venv` 安装 `socksio`。
- `OrchestratorPlanner` 现在会把 unexpected client 异常包装成 `PlannerFailure`，避免后台队列 task 直接崩溃导致前端永久停在 planning。

### 新增/修改文件
- `backend/requirements.txt` (修改)
- `backend/app/services/orchestrator_planner.py` (修改)
- `backend/tests/test_m3_planner.py` (修改)
- `docs/plans/M3_DEEPSEEK_PROXY_UNBLOCK_PLAN.md` (新增)
- `docs/plans/M3_DEEPSEEK_PROXY_UNBLOCK_CHECKLIST.md` (新增)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST 或 WebSocket 结构变更。
- 后端依赖现在支持 SOCKS 代理环境。

### 验证
- RED：新增回归测试前，普通 `ImportError` 会逃出 planner 并让后台 task 崩溃。
- `cd backend && .venv/bin/python -m pytest tests/test_m3_planner.py::test_planner_wraps_unexpected_client_errors -q` -> `1 项通过`
- `cd backend && .venv/bin/python -m pytest tests/test_m3_planner.py tests/test_m3_cli_adapters.py -q` -> `24 项通过`
- `cd backend && .venv/bin/python -c "import socksio; print('ok')"` -> `ok`

## [2026-06-02] Codex - Workspace 相对路径解析修复

### 完成内容
- 修复群聊完成后 `Orchestrator: completed` 卡片提示 `Workspace missing` 的路径不一致问题。
- 新增统一 workspace path resolver：`workspaces/...` 现在在后端各服务中一致解析到仓库根目录 `/workspaces/...`，不再因后端进程 cwd 被解析到 `backend/workspaces/...`。
- ProjectState 扫描、GitInspector 输入、WorkspaceSnapshot/audit、Artifact 写入、Preview 文件解析、OpenCode/Codex CLI cwd 均接入同一解析规则。
- 写任务分配到真实 workspace 前会确保目标目录存在，避免新建会话首次调用 CLI 时 cwd 不存在。
- 保留绝对路径和非 `workspaces/...` 临时测试路径的既有行为。

### 新增/修改文件
- `backend/app/services/workspace_paths.py` (新增)
- `backend/app/services/workspace_scanner.py` (修改)
- `backend/app/services/project_state.py` (修改)
- `backend/app/services/workspace_snapshot.py` (修改)
- `backend/app/services/artifact_service.py` (修改)
- `backend/app/services/preview_service.py` (修改)
- `backend/app/adapters/opencode.py` (修改)
- `backend/app/adapters/codex.py` (修改)
- `backend/tests/test_m3_project_state.py` (修改)
- `backend/tests/test_m3_workspace_snapshot.py` (修改)
- `backend/tests/test_m3_cli_adapters.py` (修改)
- `docs/plans/M3_WORKSPACE_PATH_RESOLUTION_PLAN.md` (新增)
- `docs/plans/M3_WORKSPACE_PATH_RESOLUTION_CHECKLIST.md` (新增)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST 或 WebSocket 结构变更。
- 行为变更：相对 `workspaces/...` 会话目录在后端服务中统一按项目根目录解析。

### 验证
- RED：新增回归测试前，ProjectState/WorkspaceSnapshot/OpenCode cwd 均解析为 `backend/workspaces/...` 并复现 `Workspace missing`。
- `cd backend && .venv/bin/python -m pytest tests/test_m3_project_state.py tests/test_m3_workspace_snapshot.py -q` -> `15 项通过`
- `cd backend && .venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q` -> `18 项通过`
- `cd backend && DEEPSEEK_API_KEY= .venv/bin/python -m pytest tests/test_m3_websocket_runtime.py tests/test_m4_artifact_preview.py -q` -> `13 项通过`
- 带本机 DeepSeek key 直接跑 runtime/preview 烟测时，1 个用例会因测试环境触发真实摘要器联网而多出 summary unavailable warning；清空 key 后离线测试通过。

## [2026-06-02] Codex - OpenCode 超时前产物保留修复

### 当前问题判断
- 手测会话 `opencode-test` 在 03:43 的代码工匠任务已不是仍在执行：数据库记录显示任务状态为 `failed`，错误为 `process timed out`。
- OpenCode 在超时前已写出 `/Users/yangyu/code/AgentHub/workspaces/opencode-test/index.html`，但旧 adapter 在 `ProcessPoolError` 分支只发 error，不扫描超时前的文件变更，因此前端没有产物卡片。

### 完成内容
- OpenCode adapter 在 `ProcessPoolError` 后会重新扫描 workspace。
- 如果检测到文件变更，会先发送一段中断摘要，再发送 `file_created` / `file_modified` 事件，最后保留 error event 让 orchestrator 标记本次执行失败。
- 这样即使 OpenCode 超时，用户也能看到超时前生成的文件卡片。

### 新增/修改文件
- `backend/app/adapters/opencode.py` (修改)
- `backend/tests/test_m3_cli_adapters.py` (修改)
- `docs/plans/M3_OPENCODE_TIMEOUT_ARTIFACT_FIX_PLAN.md` (新增)
- `docs/plans/M3_OPENCODE_TIMEOUT_ARTIFACT_FIX_CHECKLIST.md` (新增)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST 或 WebSocket 结构变更。
- OpenCode adapter 行为变更：超时/进程错误后若 workspace 已有变更，也会通过既有 artifact 事件链路展示产物。

### 验证
- RED：新增回归测试前，写出 `index.html` 后抛出 `process timed out` 只会得到 error event。
- `cd backend && .venv/bin/python -m pytest tests/test_m3_cli_adapters.py::test_opencode_adapter_emits_file_events_for_changes_written_before_timeout -q` -> `1 项通过`
- `cd backend && .venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q` -> `19 项通过`

## [2026-06-02] Codex - OpenCode 手测回归修复

### 当前问题判断
- 本轮手测新会话 `9271c0a3-e4a4-4aab-8823-1e9bc490a373` 中，代码实现任务被 DeepSeek planner 标成 `accessMode=read`，runtime 因此把 OpenCode 放到临时 read copy 中执行；OpenCode 生成了项目文件和 artifact，但真实 `workspaces/student-sign-in-system` 没有文件，导致 ProjectState 报 `Workspace missing`，预览路由返回 404。
- OpenCode stdout 里出现了非完整 JSON 的协议碎片（`part/sessionID/tokens/step-finish`），旧清洗逻辑把它当普通文本展示，造成回复框被超长串撑开。
- 前端右侧预览优先加载 `previewUrl`，当文件未落盘或历史 artifact 只有 DB 内容时会显示后端 404 JSON。

### 完成内容
- Planner normalization 现在会把明显的实现/开发/撰写/生成/保存类任务强制归一为 `write`，即使模型返回 `read`。
- 创建或更新会话时会确保相对 `workspaces/...` 目录存在；Windows 风格路径仍跳过本机 mkdir，避免在 macOS 下重新创建 `D:` 目录。
- OpenCode adapter 会过滤 malformed protocol fragments，并回落为简短执行摘要，不再把 `sessionID/tokens` 等内部协议文本推到聊天流。
- OpenCode 预览约束关键词补充“系统”，`学生课程签到系统` 这类实现任务也会被要求产出可直接预览的 `index.html`。
- 聊天正文 CSS 增加异常长串换行约束，作为 UI 兜底。
- 右侧预览面板优先使用 artifact 自带 HTML 内容作为 `srcDoc`，只有没有 HTML 内容时才请求 `previewUrl`，避免历史/临时产物直接显示 404 JSON。

### 新增/修改文件
- `backend/app/services/orchestrator_planner.py` (修改)
- `backend/app/api/conversations.py` (修改)
- `backend/app/adapters/opencode.py` (修改)
- `backend/tests/test_m3_planner.py` (修改)
- `backend/tests/test_m1_1_api.py` (修改)
- `backend/tests/test_m3_cli_adapters.py` (修改)
- `frontend/src/components/preview/IframePreview.tsx` (修改)
- `frontend/src/index.css` (修改)
- `docs/plans/M3_OPENCODE_MANUAL_TEST_REGRESSION_PLAN.md` (新增)
- `docs/plans/M3_OPENCODE_MANUAL_TEST_REGRESSION_CHECKLIST.md` (新增)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST 或 WebSocket 结构变更。
- 后端行为变更：明显会写文件的任务不会再用 read-copy workspace 执行。
- 前端行为变更：HTML artifact 优先用内嵌内容预览。

### 验证
- RED：新增测试前，代码实现任务保持 `accessMode=read`、新会话不创建 workspace、OpenCode 协议碎片会进入 `text_delta`。
- `cd backend && .venv/bin/python -m pytest tests/test_m3_planner.py tests/test_m1_1_api.py tests/test_m3_cli_adapters.py tests/test_m3_project_state.py tests/test_m3_workspace_snapshot.py tests/test_m4_artifact_preview.py -q` -> `53 项通过`
- `cd frontend && npm run build` -> 通过。

## [2026-06-02] Codex - OpenCode Review 输出兜底修复

### 当前问题判断
- 审查大师 review 任务使用 `accessMode=read` 是正确的：审查不应该写入 workspace，因此“未检测到工作区文件变更”作为 audit 事实本身没问题。
- 但用户可见回复只显示通用执行摘要是不正确的。根因是 OpenCode 本轮只返回了 read/tool/session 事件，没有返回最终审查文本，adapter 于是走了普通 fallback。

### 完成内容
- OpenCode review prompt 增加只读审查约束：不修改文件，并要求最终输出中文审查意见，包含总体结论、主要问题、改进建议。
- 当 read-only review 任务没有得到可展示文本且没有文件变更时，adapter 会基于 workspace 中的目标代码文件生成保守审查摘要，不再显示“未检测到工作区文件变更”作为用户回复。
- 兜底审查会优先看 `navigationHints.inspectFirst/changedFiles`，并对单文件 HTML、`localStorage`、`innerHTML`、表单约束、响应式断点等做轻量提示。

### 新增/修改文件
- `backend/app/adapters/opencode.py` (修改)
- `backend/tests/test_m3_cli_adapters.py` (修改)
- `docs/plans/M3_OPENCODE_REVIEW_OUTPUT_FIX_PLAN.md` (新增)
- `docs/plans/M3_OPENCODE_REVIEW_OUTPUT_FIX_CHECKLIST.md` (新增)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST 或 WebSocket 结构变更。
- OpenCode adapter 行为变更：review 任务的无文本 fallback 变为审查摘要。

### 验证
- RED：新增测试前，review 任务只返回 `OpenCode 已完成本次执行 / 未检测到工作区文件变更`。
- `cd backend && .venv/bin/python -m pytest tests/test_m3_cli_adapters.py::test_opencode_adapter_generates_review_fallback_when_review_returns_no_text -q` -> `1 项通过`
- `cd backend && .venv/bin/python -m pytest tests/test_m3_cli_adapters.py -q` -> `22 项通过`
- `cd backend && .venv/bin/python -m pytest tests/test_m3_planner.py tests/test_m1_1_api.py tests/test_m3_cli_adapters.py tests/test_m4_artifact_preview.py -q` -> `39 项通过`
- `git diff --check` -> 通过。

## [2026-06-02] Codex - Markdown Artifact 预览修复

### 当前问题判断
- 右侧 PreviewPanel header 的文件名按钮缺少收缩和省略约束，`index.html.code-review.md` 这类长文件名会挤压左侧 tab，导致 tab 文案换行。
- Markdown artifact 目前被当作普通代码文件展示，右侧“预览”tab 只支持 HTML 或 `previewUrl`，聊天流内 CodeCard 也只展示源码片段。

### 完成内容
- 新增 Markdown artifact 识别与预览模式工具，支持 `.md`、`.markdown`、`.mdown`、`.mkd` 和 `markdown/md/gfm` language。
- 新增轻量 `MarkdownPreview` 组件，用 React 节点渲染标题、段落、列表、分隔线、行内代码、加粗和 fenced code，避免 HTML 注入。
- 右侧 PreviewPanel 对 Markdown artifact 默认打开“预览”，并渲染 Markdown 文档；代码 tab 仍可查看原文。
- 聊天流 CodeCard 对 Markdown artifact 展示渲染后的文档预览，并把操作文案改为“在右侧预览”。
- PreviewPanel header 文件名按钮增加 `min-width: 0`、最大宽度和 ellipsis，tabs 固定单行不被长文件名挤换行。

### 新增/修改文件
- `frontend/src/utils/markdownPreview.ts` (新增)
- `frontend/src/components/preview/MarkdownPreview.tsx` (新增)
- `frontend/src/components/preview/PreviewPanel.tsx` (修改)
- `frontend/src/components/preview/IframePreview.tsx` (修改)
- `frontend/src/components/cards/CodeCard.tsx` (修改)
- `frontend/src/index.css` (修改)
- `frontend/tests/markdownPreview.test.mjs` (新增)
- `docs/plans/M4_MARKDOWN_PREVIEW_REGRESSION_PLAN.md` (新增)
- `docs/plans/M4_MARKDOWN_PREVIEW_REGRESSION_CHECKLIST.md` (新增)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST、WebSocket 或后端接口变更。

### 验证
- RED：新增测试前，`frontend/src/utils/markdownPreview.ts` 不存在，`npm test` 因模块缺失失败。
- `cd frontend && npm test` -> `6 项通过`
- `cd frontend && npm run build` -> 通过。
- `git diff --check` -> 通过。
- 浏览器烟测：`http://127.0.0.1:5174/workspace` 页面可加载，前端控制台 error 数为 0；未启动后端时页面有 API 404 alert，属于环境缺失。

## [2026-06-02] Codex - Markdown 表格渲染修复

### 当前问题判断
- Markdown review artifact 中的 GitHub 风格表格（`| header |` + `|---|`）被旧 parser 合并成普通 paragraph，聊天卡片和右侧预览都会显示原始表格语法。

### 完成内容
- `parseMarkdownBlocks` 新增 table block 识别，支持表头、分隔行、普通行和 `:---` / `---:` / `:---:` 对齐语法。
- `MarkdownPreview` 新增 `<table>` 渲染分支，单元格继续支持行内代码和加粗。
- Markdown 表格样式新增横向滚动、表头底色、边框和 compact 模式间距，避免窄卡片里挤压布局。

### 新增/修改文件
- `frontend/src/utils/markdownPreview.ts` (修改)
- `frontend/src/components/preview/MarkdownPreview.tsx` (修改)
- `frontend/src/index.css` (修改)
- `frontend/tests/markdownPreview.test.mjs` (修改)
- `docs/plans/M4_MARKDOWN_PREVIEW_REGRESSION_CHECKLIST.md` (修改)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST、WebSocket 或后端接口变更。

### 验证
- RED：新增表格测试前，表格内容被解析为单个 paragraph。
- `cd frontend && npm test` -> `7 项通过`
- `cd frontend && npm run build` -> 通过。
- `git diff --check` -> 通过。

## [2026-06-02] Codex - 预览控件与全屏交互优化

### 当前问题判断
- 网页预览底部的桌面/平板/手机按钮只有图标，含义不够明确；按钮与外层控制条尺寸关系不稳，在窄右栏下容易显得溢出。
- 右上角全屏按钮只切换 `fixed inset: 18px` 的放大卡片效果，没有进入真正全屏，也没有退出态文案或图标。

### 完成内容
- 新增 `previewControls` 工具配置，统一 viewport 选项与全屏按钮文案，并补测试防止回退成图标-only。
- 底部设备切换改为带“桌面 / 平板 / 手机”文字的分段控件，保留图标但增强可理解性。
- 设备切换与缩放控件的 CSS 改为稳定的 inline-flex control group，增加 gap、padding、最大宽度和 active 样式，避免溢出底部区域。
- PreviewPanel 全屏按钮改为进入/退出两态：进入时优先调用浏览器 Fullscreen API，失败时使用全视口 CSS fallback；退出时调用 `document.exitFullscreen()` 或关闭 fallback。
- 全屏样式由 `inset: 18px` 改为铺满 viewport，并补 `:fullscreen` 样式。

### 新增/修改文件
- `frontend/src/utils/previewControls.ts` (新增)
- `frontend/src/components/preview/IframePreview.tsx` (修改)
- `frontend/src/components/preview/PreviewPanel.tsx` (修改)
- `frontend/src/index.css` (修改)
- `frontend/tests/previewControls.test.mjs` (新增)
- `docs/plans/M4_PREVIEW_CONTROLS_POLISH_PLAN.md` (新增)
- `docs/plans/M4_PREVIEW_CONTROLS_POLISH_CHECKLIST.md` (新增)
- `DEVLOG.md` (修改)

### 接口变更
- 无 shared types、REST、WebSocket 或后端接口变更。

### 验证
- RED：新增测试前，`frontend/src/utils/previewControls.ts` 不存在，`npm test` 因模块缺失失败。
- `cd frontend && npm test` -> `9 项通过`
- `cd frontend && npm run build` -> 通过。
- `git diff --check` -> 通过。
- 浏览器烟测未完成：本轮 in-app Browser 返回 `Browser is not available: iab`；Vite server 已启动后停止。
## [2026-06-03] Codex - M3 Agent 链路阻塞修复

### 问题判断
- WSL/macOS 现在作为默认真实 Agent 运行环境；Windows 专属 CLI 启动行为不再是主要集成目标。
- OpenCode CLI `run --format json` 可能只输出协议事件但仍成功退出，导致前端聊天气泡展示合成兜底摘要，而不是模型文本。
- DeepSeek 直连 API 健康，但 `LLMClient.health_check()` 使用 16-token JSON 探针，导致 `deepseek-v4-flash` 返回 false。
- 审查任务可能返回有用的 Codex 文本，但如果计划为 `accessMode=write` 且没有文件变更，会被标记为失败。

### 完成内容
- 新增 `docs/plans/M3_AGENT_CHAIN_BLOCKERS_SPEC.md`、`docs/plans/M3_AGENT_CHAIN_BLOCKERS_PLAN.md` 和 `docs/plans/M3_AGENT_CHAIN_BLOCKERS_CHECKLIST.md`。
- `OpenCodeAdapter` 在生产/默认执行路径优先使用逐任务 `opencode serve` HTTP 路径，同时保留旧 CLI `run --format json` 解析器作为 fallback/测试辅助。
- 新增 server response 文本提取，跳过 reasoning/tool payload，保留 assistant 文本。
- `LLMClient.health_check()` 现在请求足够但有界的 JSON token 预算，并要求语义上的 `{"ok": true}`。
- `OrchestratorRuntime` 仍会拒绝无 workspace 变更的构建/写入任务，但允许带非空摘要的审查/审计/校验任务在无文件变更时完成。

### 修改文件
- `backend/app/adapters/opencode.py`
- `backend/app/services/llm_client.py`
- `backend/app/services/orchestrator_runtime.py`
- `backend/tests/test_m3_cli_adapters.py`
- `backend/tests/test_m3_llm_client.py`
- `backend/tests/test_m3_orchestrator_runtime.py`
- `docs/plans/M3_AGENT_CHAIN_BLOCKERS_SPEC.md`
- `docs/plans/M3_AGENT_CHAIN_BLOCKERS_PLAN.md`
- `docs/plans/M3_AGENT_CHAIN_BLOCKERS_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 无 shared type、REST 或 WebSocket 契约变更。
- 无新增依赖。
- MockAdapter 保持不变。

### 验证
- RED：新增测试最初在 `max_tokens=16`、接受 `ok:false` 健康检查、无变更审查任务失败、缺少 OpenCode server 文本提取器、缺少 `server_runner` adapter 路径等场景失败。
- WSL 定向测试：`PYTHONPATH=. python -B -m pytest -q -p no:cacheprovider tests/test_m3_llm_client.py tests/test_m3_orchestrator_runtime.py tests/test_m3_cli_adapters.py` -> `42 项通过`。
- WSL 更广 M3 测试：`PYTHONPATH=. python -B -m pytest -q -p no:cacheprovider tests/test_m3_websocket_runtime.py tests/test_m3_e2e.py` -> `12 项通过`。
- WSL 真实 Adapter 烟测：`llm_health True`；OpenCode 返回 `OPENCODE_ADAPTER_SERVER_WSL_OK`；Codex 返回 `CODEX_AFTER_FIX_WSL_OK`。
- WSL 真实群聊烟测：OpenCode 创建 `index.html` 并发出 webpage artifact；Codex 审查文本流式输出；最终 run 为 `completed`；两个任务状态完成；两个批次状态完成；无 warning。

### 队友备注
- 如果 OpenCode server 启动失败，adapter 会回退到既有 CLI 路径和既有兜底摘要。
- 后续优化可以复用 OpenCode server 进程；本次修复有意使用逐任务生命周期，保持资源归属简单、可测试。

## [2026-06-03] Codex - M3 Agent 链路共享状态 warning 修复

### 问题判断
- `AGNT_CHAIN_BLOCKERS` 改动后，真实 run 可能以 `Shared state refresh warning: 'taskId'` 结束。
- UI warning 来自 `TeamProtocolService.merge_batch()` 收到缺少 `taskId` 的失败任务结果。
- 根因：`OrchestratorRuntime.run_task()` 捕获 executor 异常后会创建兜底失败结果，但该兜底结果没有保留 Team Board 和 Project State 刷新所需的任务元数据。

### 完成内容
- 新增 RED 回归测试，覆盖 executor 异常时 `refresh_shared_state()` 批次结果保留 `taskId`、`agentId` 和 `batchId`。
- 在 audit/status 后处理前原地规范化 runtime task result 元数据，覆盖正常返回、提前失败返回和异常兜底结果，同时保留 WebSocket handler 的 `task_results` 引用，供后续 handoff audit 使用。

### 修改文件
- `backend/app/services/orchestrator_runtime.py`
- `backend/tests/test_m3_orchestrator_runtime.py`
- `docs/plans/M3_AGENT_CHAIN_BLOCKERS_PLAN.md`
- `docs/plans/M3_AGENT_CHAIN_BLOCKERS_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 无 shared type、REST、WebSocket 或前端契约变更。
- 无新增依赖。

### 验证
- RED：修复前 `tests/test_m3_orchestrator_runtime.py::test_runtime_passes_task_metadata_to_shared_refresh_when_executor_raises` 因 `KeyError: 'taskId'` 失败。
- `cd backend; python -B -m pytest -q -p no:cacheprovider tests/test_m3_orchestrator_runtime.py::test_runtime_passes_task_metadata_to_shared_refresh_when_executor_raises` -> `1 项通过`。
- `cd backend; python -B -m pytest -q -p no:cacheprovider tests/test_m3_orchestrator_runtime.py tests/test_m3_team_protocol.py tests/test_m3_project_state.py` -> `31 项通过`。
- `cd backend; python -B -m pytest -q -p no:cacheprovider tests/test_m3_llm_client.py tests/test_m3_cli_adapters.py` -> `31 项通过`。
- `cd backend; python -B -m pytest -q -p no:cacheprovider tests/test_m3_websocket_runtime.py` -> `11 项通过`。

### 队友备注
- 此 Windows workspace 中的本地 `backend/agenthub.db` 仍是旧 schema，没有 M3 run snapshot 表，因此无法从该 DB 查询截图对应的持久化 run。
- 可见的 `'taskId'` warning 已在 runtime/shared-state 边界通过自动回归测试覆盖。

## [2026-06-04] Codex - M3 Planner 校验回归测试修复

### 问题判断
- Planner catalog 校验加入后，分支测试套件里有两个过期的回归预期。
- `test_validator_rejects_nonexistent_agent_id` 期望被拒绝，但使用的 agent id 实际存在于 `available_agent_ids`。
- `test_non_mock_job_uses_deepseek_planner_wrapper` 仍按旧的双参数签名 patch `OrchestratorPlanner.plan()`，而生产代码现在会传入 `available_agent_ids`。

### 完成内容
- 修正 validator 测试 fixture，使计划任务引用一个不在可用 catalog 中、但仍是会话参与者的 agent。
- 更新 WebSocket planner wrapper fake，使其接收并断言 `available_agent_ids`。

### 修改文件
- `backend/tests/test_m3_validator.py`
- `backend/tests/test_m3_websocket_interactions.py`
- `docs/plans/M3_AGENT_CHAIN_BLOCKERS_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 无 shared type、REST、WebSocket 或前端契约变更。
- 无生产代码变更。

### 验证
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_validator.py::test_validator_rejects_nonexistent_agent_id tests/test_m3_websocket_interactions.py::test_non_mock_job_uses_deepseek_planner_wrapper` -> `2 项通过`。
- `cd backend && ../.venv/bin/python -m pytest tests/test_m3_validator.py tests/test_m3_websocket_interactions.py` -> `15 项通过`。
- `cd backend && ../.venv/bin/python -m pytest` -> `174 项通过`，有 `1 个警告` 来自 Starlette/httpx testclient deprecation。

## [2026-06-04] Codex - 自定义智能体创建 UI

### 问题判断
- 后端已有 `/agents` CRUD 和 `/platforms`，但 workspace 中没有可用的自定义 Agent 创建入口。
- 聊天顶部 `+ 添加代理` chip 是静态的，左侧栏也只能展示已有 agents。

### 完成内容
- 新增自定义 Agent 创建弹窗，包含名称、头像标记、角色/功能描述、能力标签、后端平台选择和可选角色指令。
- 将左侧栏新增 Agent 操作和聊天顶部新增 Agent 操作都接到同一个创建流程。
- 新增前端 `POST /agents` 和 `GET /platforms` API helper。
- 创建完成的 Agent 会追加到 Zustand agent store，使左侧栏立即更新。
- 补充创建和列出自定义 Agent 的后端回归测试。
- 更新 API 文档和 M3 custom-agent plan/checklist。

### 修改文件
- `backend/tests/test_m1_1_api.py`
- `frontend/src/components/chat/AgentCreateModal.tsx`
- `frontend/src/components/chat/ChatArea.tsx`
- `frontend/src/components/chat/ConversationList.tsx`
- `frontend/src/pages/Workspace.tsx`
- `frontend/src/services/api.ts`
- `frontend/src/index.css`
- `docs/API_SPEC.md`
- `docs/plans/M3_CUSTOM_AGENT_PLAN.md`
- `docs/plans/M3_CUSTOM_AGENT_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 无 shared type 变更。
- workspace UI 现在使用既有 `POST /api/v1/agents` 和 `GET /api/v1/platforms` 契约。
- 无新增依赖。

### 验证
- `cd backend && ../.venv/bin/python -m pytest tests/test_m1_1_api.py::test_create_custom_agent_persists_and_lists` -> `1 项通过`。
- `cd backend && ../.venv/bin/python -m pytest tests/test_m1_1_api.py` -> `8 项通过`。
- `cd frontend && npm test` -> `9 项通过`。
- `cd frontend && npm run build` -> 通过。
- `cd frontend && npm run lint` -> 通过。
- in-app browser 烟测 `http://localhost:5173/workspace`：打开新增 Agent 弹窗，确认平台加载，提交自定义 Agent，并确认其立即出现在左侧栏。

### 队友备注
- 创建自定义 Agent 不会自动加入当前会话；用户可在新建会话时选择它。将 Agent 加入既有会话仍是独立流程。

## [2026-06-04] Codex - 用户可见平台状态清理

### 问题判断
- 自定义 Agent 弹窗中 Codex 和 OpenCode 显示 `not_installed`，原因是平台状态来自 seed 数据，而不是运行时检查。
- Mock 仍需要作为内部 fallback/测试 Adapter，但创建自定义 Agent 时不应作为用户可见的后端平台选项。

### 完成内容
- 新增后端平台状态服务，在返回 `/platforms`、`/platforms/{id}` 和 `/platforms/{id}/healthcheck` 前刷新 platform rows。
- CLI 平台现在会先检查二进制文件是否存在，再检查 adapter health，并将结果映射为 `available`、`not_installed` 或 `error`。
- 自定义 Agent 弹窗过滤 `mock`，并默认选中第一个可用真实平台。
- 补充 Codex/OpenCode 平台状态刷新的后端回归测试。

### 修改文件
- `backend/app/api/platforms.py`
- `backend/app/services/platform_status.py`
- `backend/tests/test_m1_1_api.py`
- `frontend/src/components/chat/AgentCreateModal.tsx`
- `docs/API_SPEC.md`
- `docs/plans/M3_CUSTOM_AGENT_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 无 shared type 变更。
- `/api/v1/platforms` 现在返回刷新后的运行时状态，而不是静态 seed 状态。
- MockAdapter 仍在内部和后端契约中可用，但会从自定义 Agent 创建弹窗中隐藏。

### 验证
- `cd backend && ../.venv/bin/python -m pytest tests/test_m1_1_api.py` -> `9 项通过`。
- `cd frontend && npm test` -> `9 项通过`。
- `cd frontend && npm run lint` -> 通过。
- `cd frontend && npm run build` -> 通过。
- `curl http://localhost:8000/api/v1/platforms` -> 本机 Codex、OpenCode、LLM 和 Mock 均返回 `available`。
- in-app browser 烟测 `http://localhost:5173/workspace`：自定义 Agent 平台下拉框显示 `Codex CLI · available`、`LLM Provider (DeepSeek) · available` 和 `OpenCode CLI · available`；未出现 `Mock Agent`。

## [2026-06-04] Codex - M4 聊天与预览 UI 优化

### 问题判断
- M4 产物卡片在聊天流中过重：代码、diff、Markdown 和 iframe 预览都内联展示，而不是只放在右侧预览面板中。
- 活跃 Agent run 已有后端 `stop_generation` 契约，但 workspace UI 没有暴露停止控制。
- 三栏 workspace 布局的侧栏宽度固定，无法折叠为纯聊天视图。
- Agent 回复按纯文本渲染，导致 Markdown 语法直接显示在聊天消息中。

### 完成内容
- 将 code/file、diff、webpage 产物卡片改为紧凑摘要卡，只保留复制/打开操作；打开卡片会恢复右侧预览栏并选中对应产物。
- 当前会话存在活跃 run 时，消息输入框新增停止按钮，发送既有 WebSocket `stop_generation` 消息。
- 新增左右栏可调整宽度，以及由 Zustand UI 状态驱动的折叠/恢复控制。
- 从聊天流中隐藏 `Shared context` / TeamBoard 面板。
- 新增聊天回复 Markdown 渲染，支持标题、列表、表格、fenced code block、行内代码和加粗。
- 补充产物卡片展示和聊天 Markdown 解析的前端定向测试。

### 修改文件
- `frontend/src/components/cards/CodeCard.tsx`
- `frontend/src/components/cards/DiffCard.tsx`
- `frontend/src/components/cards/WebPreviewCard.tsx`
- `frontend/src/components/chat/ChatArea.tsx`
- `frontend/src/components/chat/MessageBubble.tsx`
- `frontend/src/components/chat/MessageInput.tsx`
- `frontend/src/components/chat/MessageMarkdown.tsx`
- `frontend/src/components/common/Layout.tsx`
- `frontend/src/pages/Workspace.tsx`
- `frontend/src/stores/uiStore.ts`
- `frontend/src/utils/artifactCard.ts`
- `frontend/src/index.css`
- `frontend/tests/artifactCard.test.mjs`
- `frontend/tests/markdownPreview.test.mjs`
- `docs/plans/M4_UI_OPTIMIZATION_PLAN.md`
- `docs/plans/M4_UI_OPTIMIZATION_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 无 shared type 变更。
- 无 REST API 变更。
- 前端现在使用既有 WebSocket `stop_generation`。
- 无新增依赖。

### 验证
- `cd frontend && npm test` -> `12 项通过`。
- `cd frontend && npm run build` -> 通过；Vite 保留 workspace bundle 既有 chunk-size warning。
- in-app browser 烟测 `http://127.0.0.1:5173/workspace`：shell、聊天区、两个 resize handle、左右折叠控制均渲染；未出现 `Shared context`；控制台无错误。由于只运行前端 dev server、未启动后端，因此出现 API toast 错误。

### 队友备注
- 面板宽度在 `uiStore` 中做了 clamp，确保中间聊天区仍可用。
- 浏览器烟测未覆盖真实后端会话；端到端 stop-generation 行为请使用正常全栈启动验证。

## [2026-06-04] Codex - M4 UI 后续修复

### 问题判断
- 折叠控制虽然可见，但位置过于靠近内容区域中部，需要移动到分隔控制位。
- 聊天 Markdown 已支持常见标题/列表/表格，但 `~~~` fence 或缩进代码块仍可能回退成普通段落。
- 后端时间戳由 naive UTC datetime 序列化，浏览器若前端不归一化，可能按本地时间解释。
- `@代理` 和 `附件` 是视觉按钮，但没有触发真实输入动作。

### 完成内容
- 将面板折叠控制移动到顶部 divider-control 区域，并居中对齐左右分隔线。
- 扩展 Markdown 解析，支持 `~~~` fenced code blocks 和缩进代码块。
- 新增 `chatUi` 格式化 helper，使无时区后端 ISO 时间戳按 UTC 处理，同时保留显式 offset 语义。
- 将 `@代理` 接到既有 mention selector，并在光标位置插入选中的 Agent mention。
- 将 `附件` 接到隐藏的多文件选择器，展示已选附件 chip，支持移除，并在发送消息文本中追加文件名/大小摘要。
- 补充时间戳归一化、附件摘要、tilde code fence 和缩进代码块的回归测试。

### 修改文件
- `frontend/src/components/chat/ChatArea.tsx`
- `frontend/src/components/chat/MessageBubble.tsx`
- `frontend/src/components/chat/MessageInput.tsx`
- `frontend/src/index.css`
- `frontend/src/utils/chatUi.ts`
- `frontend/src/utils/markdownPreview.ts`
- `frontend/tests/chatUi.test.mjs`
- `frontend/tests/markdownPreview.test.mjs`
- `docs/plans/M4_UI_OPTIMIZATION_PLAN.md`
- `docs/plans/M4_UI_OPTIMIZATION_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 无 shared type 变更。
- 无 REST 或 WebSocket 契约变更。
- 无新增依赖。
- 附件支持在 MVP 中仅限前端：选中文件的元数据会写入消息文本；文件上传/存储仍不在范围内。

### 验证
- `cd frontend && npm test` -> `17 项通过`。
- `cd frontend && npm run build` -> 通过；Vite 保留既有 workspace chunk-size warning。
- 全栈浏览器烟测 `http://127.0.0.1:5173/workspace`：shell 加载且控制台无错误；折叠控制出现在 divider-control 区域；`@代理` 打开 Agent selector；隐藏文件输入支持 `multiple`；`Shared context` 仍未出现。

### 队友备注
- 若后续产品范围需要真实二进制/文件上传，请新增后端附件契约，不要继续复用消息文本。

## [2026-06-04] Codex - M4 标注 UI 修正

### 问题判断
- 标注截图显示折叠控制应位于左侧对话栏和右侧预览栏的顶部栏区域，而不是滚动/内容区域下方。
- 高亮的 Markdown 问题是 `**\`index.html\`**` 这类嵌套行内代码：旧渲染器先匹配 strong token，保留了字面反引号，并把整个 token 都渲染成 strong 文本。

### 完成内容
- 将面板折叠控制移动到顶部栏高度（`top: 28px`），并保持居中于左右栏分隔线。
- 新增纯行内 Markdown parser，支持嵌套 strong/code token。
- 更新聊天 Markdown 渲染，使 `**\`index.html\`**` 变为包含真实 `<code>` 节点的 strong 文本，不再显示反引号。
- 补充嵌套 strong 行内代码的回归测试。

### 修改文件
- `frontend/src/components/chat/MessageMarkdown.tsx`
- `frontend/src/index.css`
- `frontend/src/utils/markdownPreview.ts`
- `frontend/tests/markdownPreview.test.mjs`
- `DEVLOG.md`

### 验证
- `cd frontend && npm test` -> `18 项通过`。
- `cd frontend && npm run build` -> 通过；Vite 保留既有 workspace chunk-size warning。
- 浏览器烟测 `http://127.0.0.1:5173/workspace`：折叠控制渲染在顶部栏高度（`y=28`），前端控制台无错误。由于本次视觉检查只运行前端 dev server，出现 API toast 错误。

## [2026-06-04] Codex - M4 面板顶部按钮位置调整

### 问题判断
- 期望的折叠按钮位置是在各面板顶部工具栏内部，而不是漂浮在面板分隔线上。
- 左侧按钮应与 AgentHub logo 行对齐，并位于左侧对话栏右边缘。
- 右侧按钮应位于预览工具栏中，紧跟全屏按钮右侧。

### 完成内容
- 将可见状态的左侧折叠控制移入 `ConversationList` 的 `sidebar__header`。
- 将可见状态的右侧折叠控制移入 `PreviewPanel` 的 `preview-toolbar`，位于全屏操作之后。
- `Layout` 中只保留隐藏面板状态的小型恢复控制，确保已折叠面板仍可重新打开。
- 移除可见状态下的全局分隔线控制。

### 修改文件
- `frontend/src/components/chat/ConversationList.tsx`
- `frontend/src/components/common/Layout.tsx`
- `frontend/src/components/preview/PreviewPanel.tsx`
- `frontend/src/index.css`
- `DEVLOG.md`

### 验证
- `cd frontend && npm test` -> `18 项通过`。
- `cd frontend && npm run build` -> 通过；Vite 保留既有 workspace chunk-size warning。
- 浏览器烟测 `http://127.0.0.1:5173/workspace`：左侧 toggle 渲染在 sidebar header 内（`right=277`，与 header 右边缘匹配）；右侧 toggle 渲染为 `全屏预览` 后的最后一个 preview toolbar 按钮；前端控制台无错误。

## [2026-06-04] Codex - M4 恢复按钮显隐行为

### 问题判断
- 两侧面板同时折叠时，始终可见的恢复按钮可能覆盖聊天标题文字。
- 当光标靠近左右顶部边缘时，恢复入口仍需要可发现。

### 完成内容
- 在顶部角落附近为折叠面板恢复按钮包裹小型边缘热区（`64px x 88px`）。
- 恢复按钮默认完全透明，隐藏时不可点击。
- 光标进入附近热区时以部分透明度显示恢复按钮；直接 hover 按钮时进一步提高透明度。
- 通过 `:focus-visible` 保留键盘焦点可见性。

### 修改文件
- `frontend/src/components/common/Layout.tsx`
- `frontend/src/index.css`
- `DEVLOG.md`

### 验证
- `cd frontend && npm test` -> `18 项通过`。
- `cd frontend && npm run build` -> 通过；Vite 保留既有 workspace chunk-size warning。
- 浏览器烟测 `http://127.0.0.1:5173/workspace`：折叠恢复按钮默认 `opacity: 0` 且 `pointer-events: none`，并具有受限的 `64 x 88` 边缘热区。

## [2026-06-04] Codex - M4 Markdown 与变更面板后续优化

### 问题判断
- 手写 Markdown 渲染器只覆盖了 Markdown 的小子集，右侧预览缺少 GFM 特性，例如 TOC 链接所需 heading anchor、blockquote、task list、strikethrough 和更完整的行内语法。
- Diff artifacts 混在右侧 Outputs 列表中，使文件变更看起来像生成产物。
- Changes tab 依赖当前 active artifact，而不是全部当前 diff artifacts，因此变更文件缺少实时感。
- 聊天产物卡片需要稳定的类 Codex 顺序：新建文件优先，编辑/变更文件靠后。

### 完成内容
- 新增前端直接依赖 `marked` 和 `DOMPurify`，用于 GFM 解析和安全 HTML 渲染。
- 将右侧 Markdown 预览和聊天 Markdown 渲染替换为共享的安全 GFM renderer。
- 为渲染后的 Markdown heading 添加 ID，使生成的 TOC 链接可以跳转到 heading。
- 新增右侧 `ChangesList`，聚合所有 diff artifacts，列出变更文件，并在用户打开前保持每个 diff 折叠。
- 从右侧 Outputs tab 中过滤 diff artifacts。
- 对聊天产物卡片排序，使 created files/web outputs 出现在 diff/change cards 之前。
- 更新 M4 plan/checklist，并补充 Markdown 渲染和 artifact 分组的回归测试。

### 修改文件
- `docs/plans/M4_UI_OPTIMIZATION_PLAN.md`
- `docs/plans/M4_UI_OPTIMIZATION_CHECKLIST.md`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/src/components/chat/MessageBubble.tsx`
- `frontend/src/components/chat/MessageMarkdown.tsx`
- `frontend/src/components/preview/ChangesList.tsx`
- `frontend/src/components/preview/MarkdownPreview.tsx`
- `frontend/src/components/preview/PreviewPanel.tsx`
- `frontend/src/index.css`
- `frontend/src/utils/artifactCard.ts`
- `frontend/src/utils/markdownPreview.ts`
- `frontend/tests/artifactCard.test.mjs`
- `frontend/tests/markdownPreview.test.mjs`
- `DEVLOG.md`

### 验证
- `cd frontend && npm test` -> `22 项通过`。
- `cd frontend && npm run build` -> 通过；Vite 保留既有 workspace chunk-size warning。
- `cd frontend && npm install --package-lock-only --ignore-scripts` -> lockfile 已是最新。
- 浏览器烟测 `http://127.0.0.1:5173/workspace`：workspace 渲染 Outputs/Preview/Code/Changes tabs，未见应用崩溃。

### 队友备注
- Markdown HTML 插入前会经过 sanitize。若未来功能需要自定义嵌入 widget，请添加严格的 DOMPurify allowlist，而不是绕过 sanitize。

## [2026-06-04] Codex - M4 产物卡片与取消后续优化

### 问题判断
- 聊天产物卡片仍显得过于繁重：展示了状态标签和复制/新标签页操作，但期望的类 Codex 流程只需要文件行和右侧预览/打开操作。
- `stop_generation` 只有在 `OrchestratorRuntime.execute()` 创建 cancel event 后才生效。queued/planning 阶段点击停止可能丢失，导致同一聊天 run 后续仍启动 Agent 工作。
- 用户可见产品文案多处使用“代理”，而期望用词是“智能体”。

### 完成内容
- 移除聊天产物卡片中的“新创建的文件”/“文件更改”等状态 badge。
- 从聊天卡片移除代码复制和网页新标签页按钮；卡片现在只保留右侧预览/打开操作。
- 将前端可见产品 UI 文案中的“代理”/“Agent”替换为“智能体”。
- 为 `OrchestratorQueue` 新增 queued-run 取消能力。
- 为 `OrchestratorRuntime` 新增执行前取消记忆，使 runtime 开始前发出的停止请求也能被遵守。
- 更新 WebSocket `stop_generation` 处理，尽可能取消 queued runs 并发布 cancelled snapshot。
- 更新 API spec、M4 plan/checklist 和后端测试，覆盖取消语义。

### 修改文件
- `docs/API_SPEC.md`
- `docs/plans/M4_UI_OPTIMIZATION_PLAN.md`
- `docs/plans/M4_UI_OPTIMIZATION_CHECKLIST.md`
- `frontend/src/components/cards/CodeCard.tsx`
- `frontend/src/components/cards/DiffCard.tsx`
- `frontend/src/components/cards/WebPreviewCard.tsx`
- `frontend/src/components/chat/AgentCreateModal.tsx`
- `frontend/src/components/chat/ChatArea.tsx`
- `frontend/src/components/chat/ConversationList.tsx`
- `frontend/src/components/chat/MentionSelector.tsx`
- `frontend/src/components/chat/MessageBubble.tsx`
- `frontend/src/components/chat/MessageInput.tsx`
- `frontend/src/components/chat/NewConversationModal.tsx`
- `frontend/src/pages/AgentManage.tsx`
- `frontend/src/pages/Workspace.tsx`
- `frontend/src/index.css`
- `frontend/src/utils/artifactCard.ts`
- `frontend/tests/artifactCard.test.mjs`
- `backend/app/services/orchestrator_queue.py`
- `backend/app/services/orchestrator_runtime.py`
- `backend/app/ws/handlers.py`
- `backend/tests/test_m3_orchestrator_runtime.py`
- `backend/tests/test_m3_websocket_runtime.py`
- `DEVLOG.md`

### 验证
- `cd frontend && npm test` -> `22 项通过`。
- `cd frontend && npm run build` -> 通过。
- `cd backend && .venv/bin/python -m pytest tests/test_m3_websocket_runtime.py -k "stop_generation"` -> `1 项通过`。
- `cd backend && .venv/bin/python -m pytest tests/test_m3_orchestrator_runtime.py -k "cancel"` -> `4 项通过`。

### 队友备注
- Planning LLM 调用不会在请求中途被强制 kill；取消现在会被记录，并阻止同一 run 后续进入 Agent 执行。

## [2026-06-04] Codex - M4 协作状态打磨

### 问题判断
- 协作面板会把每个参与者都渲染成“等待中”，同时单独展示活跃 thinking agent，因此单 Agent run 看起来像所有 Agent 都是静止且过期的。
- Orchestrator 状态卡仍使用英文标签，并将任务渲染成 `agent: title status`，读起来像日志输出而不是任务清单。
- DeepSeek summarizer 失败会存储成 project/team warning，然后出现在主状态卡里，干扰用户理解真实任务结果。

### 完成内容
- 新增前端 UI helper，用于协作 Agent 选择、状态本地化、消息本地化和 summary warning 过滤。
- 当存在 tasks/thinking 状态后，协作面板只展示参与当前 run 的智能体。
- 将“思考中”指示改为 loading spinner。
- 将 Orchestrator 卡片本地化为“主智能体”和中文状态/消息标签。
- 将 Orchestrator 任务渲染为 checklist，使用 spinner/check/error 图标和中文状态标签。
- Project State summarizer 失败时改为保留旧摘要或使用确定性本地 fallback，不再新增用户可见 warning。
- Team Board summarizer 失败时保留确定性 board 状态，不再新增用户可见 warning。
- 更新 M4 plan/checklist 和回归测试。

### 修改文件
- `docs/plans/M4_UI_OPTIMIZATION_PLAN.md`
- `docs/plans/M4_UI_OPTIMIZATION_CHECKLIST.md`
- `frontend/src/components/chat/ChatArea.tsx`
- `frontend/src/components/cards/OrchestratorStatus.tsx`
- `frontend/src/index.css`
- `frontend/src/utils/orchestratorUi.ts`
- `frontend/tests/orchestratorUi.test.mjs`
- `backend/app/services/project_state.py`
- `backend/app/services/team_protocol.py`
- `backend/tests/test_m3_project_state.py`
- `backend/tests/test_m3_team_protocol.py`
- `DEVLOG.md`

### 验证
- `cd frontend && npm test` -> `25 项通过`。
- `cd frontend && npm run build` -> 通过；Vite 保留既有 workspace chunk-size warning。
- `cd backend && .venv/bin/python -m pytest tests/test_m3_project_state.py -k "summarizer"` -> `2 项通过`。
- `cd backend && .venv/bin/python -m pytest tests/test_m3_team_protocol.py -k "summary_patch"` -> `1 项通过`。

### 队友备注
- 旧 DeepSeek failure 文本对应的已持久化 project warnings 会在前端状态卡中过滤；新的 refresh 不再写入这些 warnings。

## [2026-06-04] Codex - M4 HTML 预览全屏缩放

### 问题判断
- HTML 预览使用固定 `500px` iframe 最小高度，全屏模式下页面预览下方可能留下未使用空白。
- 预览缩放控件只支持较窄的 75% / 100% / 125% 范围，无法自由放大内部预览 viewport。

### 完成内容
- 新增共享预览缩放常量，并将范围 clamp 到 25% 到 300%。
- 将粗粒度缩放按钮替换为精细步进按钮加 range slider。
- 将预览 tab body 改为填充高度的 flex surface。
- 调整浏览器预览 viewport 尺寸计算，纳入 transform scale，使缩放后的 iframe 在视觉上填满可用 stage 高度。
- 更新全屏预览 padding，让内部预览拥有更多可用空间。

### 修改文件
- `docs/plans/M4_UI_OPTIMIZATION_PLAN.md`
- `docs/plans/M4_UI_OPTIMIZATION_CHECKLIST.md`
- `frontend/src/components/preview/IframePreview.tsx`
- `frontend/src/components/preview/PreviewPanel.tsx`
- `frontend/src/index.css`
- `frontend/src/utils/previewControls.ts`
- `frontend/tests/previewControls.test.mjs`
- `DEVLOG.md`

### 验证
- `cd frontend && npm test` -> `26 项通过`。
- `cd frontend && npm run build` -> 通过；Vite 保留既有 workspace chunk-size warning。

### 队友备注
- 缩放实现会在应用 CSS transform 前让 viewport 尺寸与 scale 成反比，因此视觉宽高保持稳定，而内部预览内容变大或变小。

## [2026-06-04] Codex - WSL 真实 Agent 链路 Codex 桥接与 Planner 覆盖修复

### 问题判断
- Windows 侧手动修复移除了可见的 `Shared state refresh warning: 'taskId'`，但 WSL 真实 run 仍会在 Codex review handoff 阶段失败。
- 根因是多层叠加：
- 运行中的 WSL 服务必须加载 `/mnt/d/AgentHub/backend`，而不是过期的 Linux clone。
- Codex 隔离 `CODEX_HOME` 放在 `/tmp` 下会被 Codex CLI helper-bin setup 拒绝。
- 将大 prompt 作为 argv 传入并隐式关闭 stdin，会让 Codex 进程行为变得脆弱。
- DeepSeek Responses bridge 丢失了关键协议细节：大型 tool output 无界转发、DeepSeek 400 body 被隐藏、thinking mode 的 `reasoning_content` 未回放、连续 Responses `function_call` items 被转换成非法 Chat Completions 消息顺序。
- Planner prompt/validation 允许明确三 Agent 的课堂签到请求坍缩成两个 generic index/README 任务。

### 完成内容
- `CodexAdapter` 现在在 `~/.cache/agenthub/codex` 或 `AGENTHUB_CODEX_HOME_ROOT` 下创建隔离 home，并通过 stdin 使用 `codex exec -` 发送 prompt。
- `ProcessPool` 现在支持显式 stdin 文本，为非交互子进程关闭 stdin，并在 stderr 为空时报告 stdout。
- `DeepSeekResponsesBridge` 现在会截断超大 tool output，包含 DeepSeek error response body，按 tool call 存储/回放 `reasoning_content`，并在 tool output 前合并连续 function calls。
- `OrchestratorPlanner` 现在执行上下文覆盖校验，当显式 mentions 或请求的需求/实现/审查/文档阶段缺失时会重规划。
- `planner_prompt` 现在明确要求保留多 Agent 分阶段工作流。
- `ws/handlers.py` 现在在复用前一次性 materialize participant/catalog scalar results，保留 available-agent 校验。
- `start_services.sh` 从 `/mnt/d/AgentHub/backend` 启动后端，并从 Linux dependency tree 启动前端，使用 `VITE_BACKEND_TARGET=http://localhost:8026`。

### 修改文件
- `backend/app/adapters/codex.py`
- `backend/app/services/deepseek_responses_bridge.py`
- `backend/app/services/orchestrator_planner.py`
- `backend/app/services/planner_prompt.py`
- `backend/app/services/process_pool.py`
- `backend/app/ws/handlers.py`
- `backend/tests/test_m3_cli_adapters.py`
- `backend/tests/test_m3_deepseek_responses_bridge.py`
- `backend/tests/test_m3_planner.py`
- `backend/tests/test_m3_process_pool.py`
- `backend/tests/test_m3_validator.py`
- `backend/tests/test_m3_websocket_interactions.py`
- `docs/plans/M3_AGENT_CHAIN_BLOCKERS_PLAN.md`
- `docs/plans/M3_AGENT_CHAIN_BLOCKERS_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 无 shared type、REST、WebSocket 或前端契约变更。
- 无新增依赖。
- MockAdapter 保持不变。

### 验证
- 先写 RED 测试，覆盖 Codex stdin/home 行为、ProcessPool stdin/stdout 错误、bridge 截断/error body/reasoning/tool-call 分组、planner mention/stage 覆盖、validator 不存在 agent 处理、WebSocket planner catalog 复用。
- WSL 变更区域测试：`PYTHONPATH=. /home/lieber/src/AgentHub/backend/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_m3_planner.py tests/test_m3_validator.py tests/test_m3_websocket_interactions.py::test_non_mock_job_uses_deepseek_planner_wrapper tests/test_m3_deepseek_responses_bridge.py tests/test_m3_process_pool.py tests/test_m3_cli_adapters.py::test_codex_adapter_uses_isolated_home_and_loopback_bridge tests/test_m3_cli_adapters.py::test_codex_adapter_emits_file_events_for_workspace_changes` -> `41 项通过`。
- WSL 直接 Codex handoff 复现前一个 task-3 review blocker：完成并输出 `text_delta`，无 `error`。
- 通过 `start_services.sh` 重启 WSL 服务；后端、前端、Vite API proxy 健康检查均返回 `200`。
- WSL 真实三 Agent 链路使用 ASCII prompt 完成四个任务：需求、预览实现、代码审查和 README；最终状态 `completed`；warnings `[]`；artifacts 包含 `index.html` webpage 和 README。
- WSL 中文 planner 烟测使用 escaped Unicode，返回需求、实现、审查、README 四阶段 ready plan。
- 后端全量测试尝试 `pytest tests` 在 304 秒后超时，未得到完整结果；上面的变更区域测试已重新运行并通过。

### 队友备注
- 中文全链路脚本失败是 PowerShell-to-WSL pipe 编码把中文变成 `????` 导致；浏览器来源的 UTF-8 输入不应走到该路径，escaped-Unicode planner 烟测已验证后端中文规划。
- 本会话 in-app Browser tool 不可用，因此用实时 HTTP/WS/API/artifact 证据替代浏览器 UI 检查。

## [2026-06-04] Codex - Planner 严格 JSON 与番茄钟稳定性修复

### 问题判断
- 番茄钟应用手测在任何 Agent 执行前失败，报错为 `DeepSeek returned invalid JSON content` 和 `Planner failed`。
- 复跑同一持久化 planner 输入时，DeepSeek planner 输出不确定：一次通过，一次错误复制 participant UUID，一次返回严格 `json.loads()` 路径无法解析的内容。
- 该失败不是 Windows/WSL 执行差异，也不是前端渲染问题；本质是 planner 输出契约和 normalization 稳定性问题。

### 完成内容
- 强化 planner prompt，明确允许的 JSON 形状、精确字段名、强制 JSON-only 输出、精确 participant `agentId` 复制规则，以及分阶段应用工作流指导。
- `LLMClient.request_json()` 现在接受 Markdown 包裹或内嵌 JSON 对象；解析仍失败时，会包含有界 raw-content preview。
- `OrchestratorPlanner` 现在会在 schema validation 前规范化常见 DeepSeek planner 变体：
- `taskId` / `task_id` / `taskID` -> `id`
- `assignedAgentId` / 相关 alias -> `agentId`
- 顶层 `dependencies` 表 -> 每个 task 的 `dependsOn`
- `readAccess` / `writeAccess` / `read` / `write` / `access` -> `accessMode`
- 当任务阶段和参与者能力上下文能明确匹配时，可修复复制错误的 invalid agent ids
- 常见应用工作流依赖会被确定性强制为 requirements -> implementation -> review -> README。
- 需求、实现、README、documentation 等会产出文档的阶段，即使模型标为 read，也会规范化为 write access。

### 修改文件
- `backend/app/services/llm_client.py`
- `backend/app/services/orchestrator_planner.py`
- `backend/app/services/planner_prompt.py`
- `backend/tests/test_m3_llm_client.py`
- `backend/tests/test_m3_planner.py`
- `docs/plans/M3_AGENT_CHAIN_BLOCKERS_PLAN.md`
- `docs/plans/M3_AGENT_CHAIN_BLOCKERS_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 无 shared type、REST、WebSocket 或前端契约变更。
- 无新增依赖。
- MockAdapter 保持不变。

### 验证
- 先写 RED 测试，覆盖 Markdown 包裹 JSON 解析、invalid JSON 诊断、宽松 planner alias、复制错误 agent id 修复、文档阶段 write access、分阶段 app DAG 强制。
- WSL 定向测试：`PYTHONPATH=. /home/lieber/src/AgentHub/backend/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_m3_llm_client.py tests/test_m3_planner.py` -> `26 项通过`。
- WSL 更广检查：
- `tests/test_m3_websocket_interactions.py` -> `7 项通过`。
- `tests/test_m3_orchestrator_runtime.py` -> `12 项通过`。
- `tests/test_m3_websocket_runtime.py` -> `11 项通过`，耗时 129.72s。
- WSL 真实番茄钟 planner-only 稳定性检查使用已持久化的失败 run 输入，10/10 次通过：`failures: []`，`badDag: []`。

### 队友备注
- 部分 planner 差异语义上仍无害，例如 review 可能根据模型是否计划写审查报告而为 `read` 或 `write`。runtime 已允许带摘要的 review/audit 任务在无文件变更时完成。
- 若未来再次出现 planner failure，前端/后端错误现在应包含有界 DeepSeek raw 内容预览，而不是只有 generic invalid JSON 消息。

## [2026-06-04] Codex - 默认 Agent 角色提示词与产品架构师流程

### 问题判断
- 三个内置 Agent 角色提示词过于简短，难以稳定塑造执行行为。
- 单一“文档专家”角色混合了承接需求/PRD/SPEC/checklist 和最终 README 写作，导致 planner 分配模糊。
- OpenCode preview-contract 检测可能把包含“系统、页面、应用”或 `index.html` 等词的文档任务误判，导致需求/文档任务创建 HTML 预览文件。

### 完成内容
- 新增内置“产品架构师”Agent，负责需求分析、PRD、项目 SPEC、checklist、计划和验收标准。
- 丰富“产品架构师、代码工匠、审查大师、文档专家”的内置提示词，补充角色边界、输出要求和 Markdown/HTML 约束。
- 更新 seed 行为，使已有内置 Agents 在 seed 时刷新 avatar、description、capabilities、system prompt 和平台绑定。
- 更新 planner prompt，支持四角色工作流：requirements -> implementation -> review -> readme。
- 新增确定性 planner 角色修正：requirements/PRD/SPEC/checklist 任务在可用时分给产品架构师，而 README/usage/setup 任务分给文档专家。
- 更新 OpenCode preview gating，使 planning/document 任务不触发强制 `index.html` 预览契约，而 implementation 任务仍会触发。
- 当 workspace snapshot warnings 包含本地超大文件时，使一个 WebSocket runtime warning 断言与环境无关。

### 修改文件
- `backend/app/services/seed.py`
- `backend/app/services/planner_prompt.py`
- `backend/app/services/orchestrator_planner.py`
- `backend/app/adapters/opencode.py`
- `backend/tests/test_m1_1_api.py`
- `backend/tests/test_m3_planner.py`
- `backend/tests/test_m3_cli_adapters.py`
- `backend/tests/test_m3_websocket_runtime.py`
- `docs/API_SPEC.md`
- `docs/plans/DEFAULT_AGENT_ROLES_PLAN.md`
- `docs/plans/DEFAULT_AGENT_ROLES_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 无 shared type、REST 或 WebSocket payload 形状变更。
- `GET /api/v1/agents` 现在 seed 四个内置 Agents，而不是三个。
- 已存在的内置 Agent 行会在 seed 时刷新为更新后的 prompt 元数据。
- 无新增依赖。
- MockAdapter 保持不变。

### 验证
- RED 定向测试先因缺少产品架构师、prompt 刷新行为过期、planner 角色分配错误、文档任务触发预览而失败。
- 实现后定向后端测试：`cd backend && .venv/bin/python -m pytest tests/test_m1_1_api.py tests/test_m3_planner.py tests/test_m3_cli_adapters.py::test_opencode_prompt_does_not_require_preview_for_document_tasks tests/test_m3_cli_adapters.py::test_opencode_prompt_requires_preview_entry_for_system_implementation_requests tests/test_m3_cli_adapters.py::test_opencode_prompt_requires_preview_entry_for_app_generation` -> `32 项通过`。
- 环境无关 fallback warning 回归测试：`cd backend && .venv/bin/python -m pytest tests/test_m3_websocket_runtime.py::test_read_task_retries_safe_execution_fallback_and_surfaces_warning` -> `1 项通过`。
- 后端全量套件：`cd backend && .venv/bin/python -m pytest` -> `197 项通过`，有 `1 个警告` 来自 Starlette/httpx testclient deprecation。
- 前端测试：`cd frontend && npm test` -> `26 项通过`。
- 前端构建：`cd frontend && npm run build` -> 通过；Vite 保留既有 chunk-size warning。

### 队友备注
- 已有本地数据库会在下次 seed 运行时（例如通过 `/api/v1/agents`）获得刷新后的内置 prompt。
- 产品架构师负责 PRD/SPEC/checklist 等规划文档；文档专家有意收窄到最终 README/usage/setup 交接文档。

## [2026-06-05] Codex - 会话添加智能体流程拆分

### 问题判断
- 侧边栏 Agent 加号和聊天头部“添加智能体”操作都打开了自定义 Agent 创建。
- 预期 UX 不同：侧边栏用于创建新的自定义 Agent，聊天头部用于将已有 Agent 添加到当前会话。

### 完成内容
- 为当前会话新增已有 Agent 选择弹窗。
- 将聊天头部“+ 添加智能体”接到当前会话 `participantIds` 更新流程。
- 保持侧边栏“常用智能体”加号接到自定义 Agent 创建流程。
- 新增前端 helper，用于过滤已参与会话的 Agents，并无重复合并 participant IDs。

### 修改文件
- `frontend/src/components/chat/AddConversationAgentsModal.tsx`
- `frontend/src/components/chat/ChatArea.tsx`
- `frontend/src/pages/Workspace.tsx`
- `frontend/src/services/api.ts`
- `frontend/src/stores/conversationStore.ts`
- `frontend/src/utils/chatUi.ts`
- `frontend/tests/chatUi.test.mjs`
- `docs/plans/M4_CONVERSATION_AGENT_PICKER_PLAN.md`
- `docs/plans/M4_CONVERSATION_AGENT_PICKER_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 无 shared type、后端或 WebSocket 契约变更。
- 前端现在使用既有 `PATCH /api/v1/conversations/{id}` 更新参与者。
- 无新增依赖。

### 验证
- 前端测试：`cd frontend && npm test` -> `28 项通过`。
- 前端构建：`cd frontend && npm run build` -> 通过；Vite 保留既有 chunk-size warning。
- 浏览器烟测：侧边栏加号打开“新增自定义智能体”；聊天头部“+ 添加智能体”为选中会话打开“添加已有智能体”。

### 队友备注
- 本次只支持向会话添加 Agents。移除参与者仍不在范围内。

## [2026-06-06] Codex - 侧边栏、产物列表与协作状态修复

### 问题判断
- 左侧对话列表时间使用了硬编码 `15:50`，没有读取会话真实时间戳。
- 自定义智能体创建入口放在“常用智能体”标题栏右侧，和“新建对话”主操作在视觉层级上不一致。
- 单条消息产物较多时会把全部产物卡片直接铺开，聊天流被产物列表淹没。
- 协作状态里 `失败` / `已阻塞` 和 `已完成` 使用相近样式，且没有展示各智能体耗时。

### 已完成
- 左侧对话时间改为格式化 `updatedAt`，缺失时回退 `createdAt` 或 `新建`。
- 将“创建智能体”移动到“新建对话”下方，使用同高度侧边栏操作按钮，并移除标题栏小加号。
- 消息产物列表默认展示前 5 个，剩余产物支持展开 / 收起。
- 前端运行态新增智能体任务计时，覆盖 thinking、running、completed、failed、blocked、cancelled 等状态，并在协作状态中展示 `耗时`。
- 协作状态新增 done / pending / danger / warning / idle 语义样式，失败为红色，阻塞为琥珀色。
- 补充了会话时间、产物折叠、协作状态 tone 与耗时的前端测试。

### 修改文件
- `frontend/src/components/chat/ConversationList.tsx`
- `frontend/src/components/chat/MessageBubble.tsx`
- `frontend/src/components/chat/ChatArea.tsx`
- `frontend/src/components/cards/OrchestratorStatus.tsx`
- `frontend/src/stores/uiStore.ts`
- `frontend/src/utils/chatUi.ts`
- `frontend/src/utils/artifactCard.ts`
- `frontend/src/utils/orchestratorUi.ts`
- `frontend/src/index.css`
- `frontend/tests/chatUi.test.mjs`
- `frontend/tests/artifactCard.test.mjs`
- `frontend/tests/orchestratorUi.test.mjs`
- `docs/plans/M5_UI_BUGFIX_PLAN.md`
- `docs/plans/M5_UI_BUGFIX_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 未修改 shared type、REST、WebSocket 或后端契约。
- 未新增依赖。

### 验证
- 交互式 zsh 下确认 Node/npm 可用：`node` 位于 `/home/yangyu/.nvm/versions/node/v24.16.0/bin/node`，`npm` 位于 `/home/yangyu/.nvm/versions/node/v24.16.0/bin/npm`。
- 前端测试：`cd frontend && zsh -lic 'npm test'` -> `31 项通过`。
- 前端构建：`cd frontend && zsh -lic 'npm run build'` -> 通过；Vite 保留既有的 chunk size warning。
- 补丁检查：`git diff --check` -> 通过。

### 队友备注
- 智能体耗时目前由前端运行态推导，因为现有 `Task` 契约没有权威耗时字段。
- 如果后端后续推送精确任务耗时，可以替换或补齐 `runtime.taskTimings`，无需调整展示组件结构。

## [2026-06-06] Codex - 右侧预览尺寸按钮窄宽修复

### 问题判断
- 右侧预览面板宽度较窄时，底部“桌面 / 平板 / 手机”切换按钮的中文标签会被挤压换行，形成逐字竖排的视觉问题。
- 该问题属于前端响应式样式问题，不涉及后端、shared types 或 WebSocket 契约。

### 完成内容
- 为预览底部控制条启用 CSS container query。
- viewport 切换按钮默认禁止文字换行，避免标签在边界宽度下被拆字。
- 当控制条宽度小于 `430px` 时自动隐藏“桌面 / 平板 / 手机”文字，仅保留图标按钮。
- 将文字 span 改为专用 `viewport-switcher__label`，避免误隐藏 Ant Design 图标的 `.anticon` span。
- 补充 `PREVIEW_VIEWPORT_LABEL_HIDE_WIDTH` 和 `PREVIEW_VIEWPORT_LABEL_CLASS` 配置与前端测试，锁定图标-only 断点和 label 作用域。

### 修改文件
- `frontend/src/components/preview/IframePreview.tsx`
- `frontend/src/index.css`
- `frontend/src/utils/previewControls.ts`
- `frontend/tests/previewControls.test.mjs`
- `docs/plans/M5_UI_BUGFIX_PLAN.md`
- `docs/plans/M5_UI_BUGFIX_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 未修改 shared type、REST、WebSocket 或后端契约。
- 未新增依赖。

### 验证
- 前端测试：`cd frontend && zsh -lic 'npm test'` -> `33 项通过`。
- 前端构建：`cd frontend && zsh -lic 'npm run build'` -> 通过；Vite 保留既有 chunk size warning。
- 补丁检查：`git diff --check` -> 通过。

## [2026-06-06] Codex - 右侧预览缩放条窄宽修复

### 问题判断
- 右侧预览面板宽度较窄时，底部缩放控件的 range slider 没有根据窗格宽度收缩，导致右侧内容被裁切。
- 原因是 slider 使用 `clamp(120px, 18vw, 240px)`，该宽度基于浏览器 viewport，而不是右侧预览窗格/控制条自身宽度。

### 完成内容
- 将 `zoom-switcher` 改为可收缩 flex 项，按预览底部控制条剩余空间布局。
- 将 range slider 改为 `flex: 1 1 56px`，宽度使用 `100%` 和 `max-width: 180px`，不再依赖 `vw`。
- 在窄控制条下压缩缩放按钮和百分比文本宽度，保证 `- / 百分比 / slider / +` 尽量完整显示。
- 补充 `PREVIEW_ZOOM_SLIDER_MIN_WIDTH` 配置与测试，锁定窄宽最小 slider 宽度。

### 修改文件
- `frontend/src/index.css`
- `frontend/src/utils/previewControls.ts`
- `frontend/tests/previewControls.test.mjs`
- `docs/plans/M5_UI_BUGFIX_PLAN.md`
- `docs/plans/M5_UI_BUGFIX_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 未修改 shared type、REST、WebSocket 或后端契约。
- 未新增依赖。

### 验证
- 前端测试：`cd frontend && zsh -lic 'npm test'` -> `34 项通过`。
- 前端构建：`cd frontend && zsh -lic 'npm run build'` -> 通过；Vite 保留既有 chunk size warning。
- 补丁检查：`git diff --check` -> 通过。

## [2026-06-06] Codex - 右侧预览缩放条宽窗格空白修复

### 问题判断
- 上一版为了修复窄窗格裁切，将 `zoom-switcher` 设置为 `flex: 1`，导致右侧预览窗格较宽时缩放控件占满剩余空间，slider 右侧出现大面积空白。
- 期望行为是宽窗格下缩放控件保持内容紧凑，窄窗格下仍可自动收缩。

### 完成内容
- 将 `zoom-switcher` 从 `flex: 1 1 0` 改为 `flex: 0 1 340px`，宽窗格下不再主动占满剩余空间。
- 为缩放控件增加 `max-width: min(100%, 340px)`，保证宽时紧凑、窄时跟随容器收缩。
- 补充 `PREVIEW_ZOOM_CONTROL_MAX_WIDTH` 配置与测试，锁定宽窗格最大紧凑宽度。

### 修改文件
- `frontend/src/index.css`
- `frontend/src/utils/previewControls.ts`
- `frontend/tests/previewControls.test.mjs`
- `docs/plans/M5_UI_BUGFIX_PLAN.md`
- `docs/plans/M5_UI_BUGFIX_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 未修改 shared type、REST、WebSocket 或后端契约。
- 未新增依赖。

### 验证
- 前端测试：`cd frontend && zsh -lic 'npm test'` -> `35 项通过`。
- 前端构建：`cd frontend && zsh -lic 'npm run build'` -> 通过；Vite 保留既有 chunk size warning。
- 补丁检查：`git diff --check` -> 通过。

## [2026-06-06] Codex - 工作目录名称与生成项目端口安全优化

### 问题判断
- 新建对话表单要求用户理解并输入 `workspaces/xxx`，裸目录名会被后端拒绝，体验不友好。
- 生成项目可能写入 `server.open` / `open: true` 或硬编码 `5173`，导致运行生成项目时自动弹浏览器窗口并与 AgentHub 主前端端口混淆。

### 完成内容
- 后端 `workDir` 规范化支持裸目录名：`todo-app` 会保存为 `workspaces/todo-app`，空值仍自动生成唯一目录，逃逸路径仍拒绝。
- 新建对话弹窗将“工作目录（留空自动生成）”改为“工作目录名称”，placeholder 改为直接输入 `todo-app` 的心智模型。
- 前端提交时统一把目录名补成 `workspaces/<name>`，保留已输入 `workspaces/<name>` 的兼容行为。
- OpenCode/Codex Adapter 增加生成项目前端 dev-server prompt 约束：不设置 `server.open` / `open: true`，不硬编码 AgentHub 端口，验证优先用 build/test/typecheck。
- WebSocket 测试改用项目内相对 workspace 并清理临时目录，避免完整测试后留下 `D:/` 残留。

### 修改文件
- `backend/app/adapters/prompt_contracts.py`
- `backend/app/adapters/opencode.py`
- `backend/app/adapters/codex.py`
- `backend/app/api/conversations.py`
- `backend/app/schemas/conversation.py`
- `backend/tests/test_m1_1_api.py`
- `backend/tests/test_m1_2_websocket.py`
- `backend/tests/test_m3_cli_adapters.py`
- `frontend/src/components/chat/NewConversationModal.tsx`
- `frontend/src/utils/chatUi.ts`
- `frontend/tests/chatUi.test.mjs`
- `docs/API_SPEC.md`
- `docs/plans/M5_WORKSPACE_PREVIEW_SAFETY_PLAN.md`
- `docs/plans/M5_WORKSPACE_PREVIEW_SAFETY_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- `CreateConversationDTO.workDir` 类型未变，仍为字符串。
- REST 创建/更新会话现在接受裸工作目录名并规范化到 `workspaces/` 下；API 文档已同步。
- 未新增依赖。

### 验证
- 目标后端测试：`python -m pytest backend/tests/test_m1_1_api.py::test_create_conversation_accepts_workspace_folder_name backend/tests/test_m1_1_api.py::test_create_conversation_rejects_workspace_name_that_escapes_root backend/tests/test_m3_cli_adapters.py::test_opencode_prompt_requires_preview_entry_for_app_generation backend/tests/test_m3_cli_adapters.py::test_codex_prompt_includes_generated_project_dev_server_safety` -> `4 项通过`。
- 相关后端套件：`python -m pytest backend/tests/test_m1_1_api.py backend/tests/test_m3_cli_adapters.py` -> `39 项通过`。
- 完整后端测试：`python -m pytest backend/tests` -> `200 项通过`。
- 前端测试：`npm test` -> `36 项通过`。
- 前端构建：`npm run build` -> 通过；Vite 保留既有 chunk size warning。

## [2026-06-06] Codex - 关闭高风险写入审批弹窗

### 问题判断
- 代码工匠创建/修改较多文件，或 Planner 标记配置文件、删除/重命名风险时，Orchestrator 会进入 `awaiting_approval` 并显示 `Allow execution` 审批卡。
- 用户确认 Agent 都在工作区内执行，希望完全放开这些写操作，不再出现“是否允许执行 / 高危写入许可”弹窗。

### 完成内容
- 移除 Orchestrator 高风险写入审批触发条件：`mayDeleteOrRenameFiles`、`mayTouchConfigFiles`、`estimatedFilesTouched > 10` 均不再阻塞执行。
- 保留 shared WebSocket 类型与前端审批卡兼容代码，但当前后端策略不再推送 `orchestrator_approval_required`。
- 将原审批恢复测试改为风险写任务直接执行回归测试，并补充 helper 断言，确保风险 hints 不再生成审批原因。
- API 文档标注审批消息为兼容保留、当前正常流程不再要求用户审批。

### 修改文件
- `backend/app/ws/handlers.py`
- `backend/tests/test_m3_websocket_interactions.py`
- `docs/API_SPEC.md`
- `docs/plans/M5_DISABLE_WRITE_APPROVAL_PLAN.md`
- `docs/plans/M5_DISABLE_WRITE_APPROVAL_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 未修改 `packages/shared/types.ts`。
- `orchestrator_approval_required` / `orchestrator_approval_response` 协议兼容保留，但后端不再因工作区写入风险主动发起审批。
- 未新增依赖。

### 验证
- 先跑新目标测试确认旧逻辑红灯：`backend/.venv/bin/python -m pytest backend/tests/test_m3_websocket_interactions.py::test_risky_write_plan_executes_without_approval_prompt backend/tests/test_m3_websocket_interactions.py::test_approval_response_without_paused_job_returns_error backend/tests/test_m3_websocket_interactions.py::test_risky_write_tasks_do_not_have_elevated_approval_reason` -> `2 项失败，1 项通过`。
- 修改后目标测试：同上命令 -> `3 项通过`。
- 相关后端套件：`backend/.venv/bin/python -m pytest backend/tests/test_m3_websocket_interactions.py` -> `8 项通过`。
- 补丁检查：`git diff --check` -> 通过。

## [2026-06-06] Codex - 移除 accessMode 运行时读写权限语义

### 问题判断
- `accessMode` 读写划分在当前 MVP 中已经不再提供实际安全收益，反而会导致 Planner 中文任务归类误判后触发 read copy、写任务无变更失败、审查 fallback 不生效等问题。
- 用户确认 Agent 都在项目工作区内执行，希望不再因为读写权限判断导致审查或后续任务误失败。

### 完成内容
- Scheduler 不再限制同一批只能有一个 `write` 任务；现在只保留依赖顺序、同一 Agent 不并行和单批最多 3 个任务。
- Runtime 不再根据 `accessMode` 创建 read copy；所有任务都使用真实会话工作区执行。
- Runtime 移除“写任务成功但无文件变更 => failed”的校验，审查/文档/文本总结不再因此被误判失败。
- Handoff 的 workspace access metadata 统一为 `write`，避免下游 Adapter 继续按旧读写权限分支。
- OpenCode review fallback 和 preview contract 不再以 `accessMode` 为开关，改为按任务文本意图识别。
- dev-server prompt safety contract 不再要求写权限才注入。
- API 文档补充：`accessMode` 为兼容保留的计划元数据，不再作为执行权限。

### 修改文件
- `backend/app/services/orchestrator_scheduler.py`
- `backend/app/services/orchestrator_runtime.py`
- `backend/app/services/handoff_builder.py`
- `backend/app/adapters/opencode.py`
- `backend/app/adapters/prompt_contracts.py`
- `backend/tests/test_m3_scheduler.py`
- `backend/tests/test_m3_orchestrator_runtime.py`
- `backend/tests/test_m3_websocket_runtime.py`
- `backend/tests/test_m3_cli_adapters.py`
- `backend/tests/test_m3_handoff_builder.py`
- `docs/API_SPEC.md`
- `docs/plans/M5_REMOVE_ACCESS_MODE_RUNTIME_PLAN.md`
- `docs/plans/M5_REMOVE_ACCESS_MODE_RUNTIME_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 未修改 `packages/shared/types.ts`，`Task.accessMode` 字段继续保留以兼容已有 Planner schema、WebSocket 快照和前端类型。
- 后端执行语义变化：`accessMode` 不再影响权限、workspace 隔离、并发或成功/失败判定。
- 未新增依赖。

### 验证
- 新回归测试先红灯：目标测试组在旧逻辑下 `7 项失败，1 项通过`，覆盖 scheduler、runtime workspace、no-change 失败、handoff metadata、OpenCode review fallback、preview/dev-server contract。
- 受影响后端套件：`backend/.venv/bin/python -m pytest backend/tests/test_m3_scheduler.py backend/tests/test_m3_orchestrator_runtime.py backend/tests/test_m3_handoff_builder.py backend/tests/test_m3_websocket_runtime.py backend/tests/test_m3_cli_adapters.py` -> `57 项通过`。
- 完整后端测试：`backend/.venv/bin/python -m pytest backend/tests` -> `203 项通过`。

## [2026-06-06] Codex - 产物卡片列表折叠与预览优先排序

### 问题判断
- 复杂项目会产生大量文件产物，如果聊天流逐个展示会挤占对话空间。
- 当前产物列表已有折叠能力，但默认展示 5 个；排序也会把普通代码文件排在 HTML/README 等更适合预览的内容前面。

### 完成内容
- 将消息内产物卡片默认展示数量从 5 个调整为 3 个，剩余产物通过“展开剩余 N 个产物”查看。
- 新增稳定的产物优先级排序：网页/预览链接、HTML 文件、README/Markdown、其他文档/文件、普通代码、Diff。
- 保留同优先级产物的原始到达顺序，避免列表在流式追加时出现不必要的重排。
- `MessageBubble` 使用 artifact helper 返回的隐藏数量，避免组件重复计算折叠数量。
- 扩展 artifact card 纯逻辑测试，覆盖三卡折叠、HTML/README 优先、Diff 后置和稳定排序。

### 修改文件
- `frontend/src/utils/artifactCard.ts`
- `frontend/src/components/chat/MessageBubble.tsx`
- `frontend/tests/artifactCard.test.mjs`
- `docs/plans/M5_ARTIFACT_LIST_PRIORITIZATION_PLAN.md`
- `docs/plans/M5_ARTIFACT_LIST_PRIORITIZATION_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 未修改 `packages/shared/types.ts`。
- 未修改 REST、WebSocket 或后端 artifact payload。
- 未新增依赖。

### 验证
- RED 测试确认旧逻辑失败：`cd frontend && npm test` -> `4 项失败`，覆盖网页优先、HTML/README 优先、默认 3 个和折叠后优先级展示。
- 修改后前端测试：`cd frontend && npm test` -> `39 项通过`。
- 前端构建：`cd frontend && npm run build` -> 通过；Vite 保留既有 chunk size warning。
- 补丁检查：`git diff --check` -> 通过。
- 未单独运行浏览器手工 smoke；多产物折叠和排序已由 `frontend/tests/artifactCard.test.mjs` 覆盖。

## [2026-06-06] Codex - Planner 语义分配改为 LLM 优先

### 问题判断
- 当前 Planner 归一化会先用关键词阶段识别覆盖合法 `agentId`，例如“电商页面需求分析与规划”被“页面”关键词误判为实现任务，导致产品架构师任务被改派给代码工匠。
- `accessMode` 已不再控制运行时权限，继续用关键词把显式 `read` 强制改成 `write` 会制造不必要误判。

### 完成内容
- `_resolve_agent_id()` 现在先信任属于当前 participants 的合法 `agentId`，只有缺失或非法时才按 `agentName`、nested agent object、阶段/profile fallback 修复。
- 阶段关键词逻辑降级为兜底，不再覆盖 LLM 的合法语义分配。
- 显式 `accessMode` 只做大小写归一化，不再被 `_looks_like_write_task()` 或 `_stage_implies_write()` 强制从 `read` 改成 `write`。
- 扩展 Planner 测试，覆盖电商页面四智能体、审查任务歧义文本、agentName 冲突、非法 id 修复、accessMode 保留和真实遗漏显式 @ agent。

### 修改文件
- `backend/app/services/orchestrator_planner.py`
- `backend/tests/test_m3_planner.py`
- `docs/API_SPEC.md`
- `docs/plans/M5_LLM_FIRST_PLANNER_PLAN.md`
- `docs/plans/M5_LLM_FIRST_PLANNER_CHECKLIST.md`
- `DEVLOG.md`

### 接口变化
- 未修改 `packages/shared/types.ts`。
- 未修改 REST、WebSocket 或前端 UI 协议。
- Planner 行为变化：合法 participant `agentId` 由 LLM 输出主导，后端只做低侵入修复和结构校验。

### 验证
- 新增测试先红灯：`PYTHONPATH=backend backend/.venv/bin/python -m pytest backend/tests/test_m3_planner.py -q` -> `4 项失败，19 项通过`。
- 修改后目标测试：`PYTHONPATH=backend backend/.venv/bin/python -m pytest backend/tests/test_m3_planner.py -q` -> `23 项通过`。
- 编排 smoke：`backend/.venv/bin/python -m pytest backend/tests/test_m3_planner.py backend/tests/test_m3_websocket_interactions.py backend/tests/test_m3_websocket_runtime.py -q` -> `42 项通过`。
- 完整后端测试：`backend/.venv/bin/python -m pytest backend/tests` -> `208 项通过，1 个警告`。
- 补丁检查：`git diff --check` -> 通过。
- 未重复浏览器手测电商页面；新增 planner 回归测试已覆盖同一类“页面 + 需求”导致产品架构师缺失的失败路径。

## [2026-06-06] Codex - 停止生成支持取消暂停中的单聊任务

### 问题判断
- 当前单聊任务暂停在澄清或审批阶段时，停止生成按钮可能失效。
- 后端 `stop_generation` 只会取消正在执行或排队中的任务；暂停任务会留在 `paused_jobs`，且不会推送 `cancelled` 快照。

### 完成内容
- 新增 WebSocket 取消辅助逻辑，覆盖运行中、排队中和暂停中的任务。
- 处理运行态与暂停态竞态：任务已推送 `awaiting_input`，但队列 worker 尚未释放运行槽位。
- 增加回归测试，证明暂停中的单聊任务可被取消，且取消后不能继续恢复。
- 更新 API 规范中 `stop_generation` 对暂停任务的语义说明。

### 新增/修改文件
- `backend/app/ws/handlers.py`
- `backend/tests/test_m3_websocket_runtime.py`
- `docs/API_SPEC.md`
- `docs/plans/M4_STOP_GENERATION_PAUSED_RUN_PLAN.md`
- `docs/plans/M4_STOP_GENERATION_PAUSED_RUN_CHECKLIST.md`
- `DEVLOG.md`

### 接口变更
- 无 WebSocket payload 结构或共享类型变化。
- `stop_generation` 现在也会取消暂停在 `awaiting_input` / `awaiting_approval` 的任务。
- 无新增依赖。

### 验证
- 回归测试先红灯，等待 `cancelled` 时卡住，与反馈问题一致。
- 定向测试： `cd backend && ../.venv/bin/python -m pytest -vv tests/test_m3_websocket_runtime.py::test_stop_generation_cancels_paused_input_run tests/test_m3_websocket_runtime.py::test_stop_generation_cancels_active_run` -> `2 项通过`，`1 个警告`。
- WebSocket 运行时烟测： `cd backend && ../.venv/bin/python -m pytest tests/test_m3_websocket_runtime.py` -> `12 项通过`，`1 个警告`。

### 给其他成员的提醒
- 前端按钮接线保持不变，会直接受益于后端更完整的取消语义。

## [2026-06-06] Codex - Vite HTML 预览支持构建产物资源

### 问题判断
- 生成的 Vite 项目可能产出 `dist/index.html`，其中包含 `/assets/app.js` 这类根相对资源地址。
- 右侧预览此前对 HTML 产物优先使用 iframe `srcDoc`，导致资源会按 AgentHub 前端源解析，而不是按会话预览路由解析。
- 即使打开 `/preview/{conversation}/dist/index.html`，后端 HTML 响应也会原样返回 Vite 根相对资源地址。

### 完成内容
- 带 `previewUrl` 的前端 HTML 产物现在通过 iframe `src` 加载，让预览路由成为文档 URL。
- 后端预览 HTML 响应会把根相对 `src` / `href` 资源地址改写到当前预览目录，例如 `/assets/app.js` -> `/preview/{conversation}/dist/assets/app.js`。
- 增加前后端定向回归测试，覆盖 Vite 风格构建后 HTML 预览。
- 更新 Preview API 文档，说明资源地址改写行为。

### 新增/修改文件
- `backend/app/services/preview_service.py`
- `backend/tests/test_m1_1_api.py`
- `frontend/src/components/preview/IframePreview.tsx`
- `frontend/src/utils/markdownPreview.ts`
- `frontend/tests/markdownPreview.test.mjs`
- `docs/API_SPEC.md`
- `docs/plans/M5_VITE_HTML_PREVIEW_FIX_PLAN.md`
- `docs/plans/M5_VITE_HTML_PREVIEW_FIX_CHECKLIST.md`
- `DEVLOG.md`

### 接口变更
- 无共享类型、REST payload 或 WebSocket payload 结构变化。
- 现有 `/preview/{conversation_id}/{file_path}` 路由现在会改写 HTML 资源地址，以保证预览正确。
- 无新增依赖。

### 验证
- 回归测试先红灯，表现为缺少前端辅助逻辑，且后端 HTML 中 `/assets/*` 未被改写。
- 前端定向/完整测试： `cd frontend && npm test` -> `40 项通过`.
- 后端预览/API 定向测试： `cd backend && ../.venv/bin/python -m pytest tests/test_m1_1_api.py tests/test_m3_websocket_runtime.py::test_group_opencode_preview_request_emits_webpage_artifact` -> `14 项通过`，`1 个警告`。

### 给其他成员的提醒
- 该修复面向已构建的 Vite 静态产物，不会启动生成项目的 Vite dev server。

## [2026-06-07] M5 前端视觉刷新

### 完成内容
- 按用户提供的 Claude-inspired 设计资料，将前端全局视觉 token、三栏工作台、聊天流、产物卡、输入区、预览面板和 Markdown/code 容器统一为暖纸色、ivory 面板、terracotta 主行动色、serif 标题和 ring shadow 风格。
- 新增样式守护测试，确保核心设计 token 存在并限制旧的渐变式 chrome 回流。
- 新增本次改造的 plan/checklist，保持 AgentHub 模块化协作流程。

### 新增/修改文件
- `docs/plans/M5_FRONTEND_DESIGN_REFRESH_PLAN.md` (新增)
- `docs/plans/M5_FRONTEND_DESIGN_REFRESH_CHECKLIST.md` (新增)
- `frontend/src/index.css` (修改)
- `frontend/tests/designTokens.test.mjs` (新增)
- `DEVLOG.md` (修改)

### 接口变更
- 无接口变更；未修改 `packages/shared/types.ts` 或 `docs/API_SPEC.md`。

### 下一步
- 浏览器桌面与窄屏烟测已完成；后续若继续细化，可针对弹窗和空状态再做一次视觉微调。

### 给其他成员的提醒
- @小马：本次只改前端样式，不影响 Adapter、API 或 WebSocket 契约。
- @组长：预览面板、代码/Markdown/diff 容器已换成 warm token；后续新增预览控件请优先复用 `frontend/src/index.css` 的 design tokens。

## [2026-06-07] Codex - 左侧边栏滚动修复

### 问题判断
- 左侧栏长内容会被裁切，因为会话列表没有稳定占满剩余 flex 高度。
- 内置/自定义 Agent 列表过长时会占满侧边栏垂直空间，把会话列表压到 0 高度，导致会话不可达。

### 完成内容
- 为侧边栏增加明确的滚动容器约束。
- 限制常用 Agent 列表高度，并让它可以独立滚动。
- 让会话列表占据剩余空间，并保留自己的纵向滚动。
- 增加 CSS 回归测试，覆盖侧边栏和列表滚动约束。

### 新增/修改文件
- `frontend/src/index.css`
- `frontend/tests/sidebarLayout.test.mjs`
- `docs/plans/M5_UI_BUGFIX_PLAN.md`
- `docs/plans/M5_UI_BUGFIX_CHECKLIST.md`
- `DEVLOG.md`

### 接口变更
- 无 API、WebSocket、共享类型或依赖变化。

### 验证
- 回归测试先红灯，问题是缺少 `.conversation-list` flex 尺寸约束。
- `cd frontend && npm test` -> `44 项通过`.
- `cd frontend && npm run build` -> 通过, 带有既有 Vite chunk-size 警告.
- 浏览器烟测 `http://127.0.0.1:5174/workspace`：20 条会话时，`.conversation-list` 具备 `overflow-y: auto`、正高度，滚轮可将 `scrollTop` 从 `0` 改到 `620`。

### 给其他成员的提醒
- 该修复仅涉及 CSS，并限制在左侧边栏布局内，不应影响聊天、预览、后端或 Adapter 行为。

## [2026-06-07] Codex - 工作台体验打磨与自定义 Agent 管理

### 问题判断
- 工作台空状态暴露了 Mock 实现文案，右侧预览在没有产物时显示了“不支持网页”的提示。
- Markdown 预览在全屏时仍保留卡片式间距，没有充分利用面板空间。
- 运行耗时来自前端本地时间戳，刷新触发的快照可能生成误导性的全新计时。
- 后端已经支持自定义 Agent CRUD，但 `/agents` 仍是占位页面。

### 完成内容
- 将工作台和预览空状态替换为面向产品体验的文案。
- 没有激活产物时，右侧面板默认显示产物列表。
- 增加全屏 Markdown CSS，让 Markdown 预览填满预览主体。
- 调整运行耗时逻辑，避免没有本地开始事件的状态快照在刷新后生成假耗时。
- 实现 `/agents` 页面，包含自定义/内置分区、创建弹窗复用、自定义 Agent 删除流程和工作台侧边栏入口。
- 增加前端回归测试，覆盖文案、Markdown 全屏样式、Agent 管理能力和刷新耗时。

### 新增/修改文件
- `frontend/src/components/chat/ChatArea.tsx`
- `frontend/src/components/chat/ConversationList.tsx`
- `frontend/src/components/preview/IframePreview.tsx`
- `frontend/src/components/preview/PreviewPanel.tsx`
- `frontend/src/pages/AgentManage.tsx`
- `frontend/src/services/api.ts`
- `frontend/src/stores/agentStore.ts`
- `frontend/src/stores/uiStore.ts`
- `frontend/src/index.css`
- `frontend/tests/experiencePolish.test.mjs`
- `frontend/tests/runtimeStore.test.mjs`
- `docs/plans/M5_UI_BUGFIX_PLAN.md`
- `docs/plans/M5_UI_BUGFIX_CHECKLIST.md`
- `DEVLOG.md`

### 接口变更
- 无 REST、WebSocket 或共享类型契约变化。
- 前端 API client 现在暴露既有 `PATCH /agents/{id}` 和 `DELETE /agents/{id}` 辅助方法。
- 无新增依赖。

### 验证
- 回归测试先红灯，覆盖旧空状态文案、缺失的全屏 Markdown CSS、占位 Agent 页面和刷新产生假耗时。
- `cd frontend && npm test` -> `48 项通过`.
- `cd frontend && npm run build` -> 通过。
- 浏览器烟测 `http://127.0.0.1:5174/workspace` 和 `/agents`：旧文案已消失，产物空状态可见，Agent 管理页可访问，自定义/内置分区渲染正常，自定义删除按钮存在。

### 给其他成员的提醒
- 内置 Agent 在 UI 和后端都保持不可删除，以保留种子角色和 Mock-first 工作流。

## [2026-06-08] Codex - Vite 预览、运行耗时与侧边栏清理

### 问题判断
- Vite 源码项目不能通过静态服务 `index.html` 预览，因为 `/src/*.tsx`、Vite 转换和开发态模块 URL 依赖 `npm run dev`。
- Agent 耗时展示仍依赖前端本地计时，刷新后可能丢失或扭曲已耗时长。
- 左侧边栏搜索框存在异常，且当前 MVP 不需要该入口。
- 会话行和左侧栏默认宽度偏松，不利于高频浏览。

### 完成内容
- 增加后端 Vite 工作区识别、按需启动 `npm run dev`、`/preview/{conversation_id}/*` 代理、绝对 URL 改写和派生 dev server 生命周期清理。
- 在 Orchestrator 运行时快照中增加以后端为准的任务 `startedAt` / `endedAt` 时间戳。
- 更新共享 `Task` 和 `API_SPEC.md`，记录耗时字段。
- 前端运行耗时展示改为只使用后端任务时间戳。
- 移除侧边栏搜索 UI、状态和请求接线。
- 压缩左侧栏默认宽度、拖拽范围和会话行间距。

### 新增/修改文件
- `backend/app/main.py`
- `backend/app/services/preview_service.py`
- `backend/app/services/orchestrator_runtime.py`
- `backend/tests/test_m3_orchestrator_runtime.py`
- `backend/tests/test_m4_artifact_preview.py`
- `frontend/src/components/chat/ConversationList.tsx`
- `frontend/src/pages/Workspace.tsx`
- `frontend/src/stores/uiStore.ts`
- `frontend/src/index.css`
- `frontend/tests/runtimeStore.test.mjs`
- `frontend/tests/sidebarLayout.test.mjs`
- `packages/shared/types.ts`
- `docs/API_SPEC.md`
- `docs/plans/M5_VITE_HTML_PREVIEW_FIX_PLAN.md`
- `docs/plans/M5_VITE_HTML_PREVIEW_FIX_CHECKLIST.md`
- `docs/plans/M5_UI_BUGFIX_PLAN.md`
- `docs/plans/M5_UI_BUGFIX_CHECKLIST.md`
- `DEVLOG.md`

### 接口变更
- `Task` 现在允许可选的 `startedAt` 和 `endedAt` ISO 时间戳。
- 现有 `/preview/{conversation_id}/{file_path}` URL 保持不变；Vite dev-server 代理属于内部实现。
- 无新增 npm 或 pip 依赖。

### 验证
- `cd backend && .venv/bin/python -m pytest tests/test_m3_orchestrator_runtime.py tests/test_m4_artifact_preview.py` -> `19 项通过`，带有 Starlette TestClient 既有 `httpx` 弃用警告.
- `cd frontend && npm test -- runtimeStore.test.mjs sidebarLayout.test.mjs` -> `51 项通过`.
- `cd frontend && npm run build` -> 通过。

### 给其他成员的提醒
- Vite 预览要求生成工作区具备可运行的 npm 依赖，这与用户本地执行 `npm run dev` 的预期一致。
- 后端 `GET /conversations?...&search=` 兼容性保留；仅移除了前端损坏的左侧搜索入口。

## [2026-06-08] Codex - 回滚侧边栏紧凑化

### 问题判断
- 上一轮针对问题 4 的侧边栏紧凑化不是期望方向。
- Vite 预览、后端计时和搜索移除修复应继续保留。

### 完成内容
- 将左侧栏默认宽度从 `260px` 恢复到 `300px`。
- 将左侧栏拖拽范围从 `220-360px` 恢复到 `240-440px`。
- 恢复侧边栏 padding/gap 和会话行高度/padding 到之前布局。
- 调整侧边栏回归测试，仅保留搜索移除断言。
- 更新 M5 UI 修复 plan/checklist，移除紧凑行范围。

### 新增/修改文件
- `frontend/src/stores/uiStore.ts`
- `frontend/src/index.css`
- `frontend/tests/sidebarLayout.test.mjs`
- `docs/plans/M5_UI_BUGFIX_PLAN.md`
- `docs/plans/M5_UI_BUGFIX_CHECKLIST.md`
- `DEVLOG.md`

### 接口变更
- 无 API、WebSocket、共享类型或依赖变化。

### 验证
- `cd frontend && npm test -- sidebarLayout.test.mjs runtimeStore.test.mjs` -> `51 项通过`.
- `cd frontend && npm run build` -> 通过。
- `git diff --check` -> 通过。

## [2026-06-08] Codex - 修复会话行被拉伸

### 问题判断
- 红框标注的会话行变得过大，因为 `.conversation-list` 会作为 CSS grid 填满侧边栏剩余高度。
- 当会话较少时，grid 自动行会拉伸并占据额外垂直空间。

### 完成内容
- 为 `.conversation-list` 增加 `align-content: start`，让额外高度留在行下方。
- 增加 `grid-auto-rows: max-content`，让每个会话行保持内容高度。
- 增加侧边栏回归测试，覆盖会话行拉伸场景。

### 新增/修改文件
- `frontend/src/index.css`
- `frontend/tests/sidebarLayout.test.mjs`
- `docs/plans/M5_UI_BUGFIX_PLAN.md`
- `docs/plans/M5_UI_BUGFIX_CHECKLIST.md`
- `DEVLOG.md`

### 接口变更
- 无 API、WebSocket、共享类型或依赖变化。

### 验证
- `cd frontend && npm test -- sidebarLayout.test.mjs` -> `52 项通过`.
- `cd frontend && npm run build` -> 通过。
- `git diff --check` -> 通过。

## [2026-06-08] Codex - 将 LLM 规划范围限制到被提及的调度 Agent

### 问题判断
- 在非 mock 群聊任务中，显式 `@` 已将执行用的 `job["agents"]` 缩小，但 `plan_job()` 仍把所有会话参与者暴露给 LLM planner。
- planner 可能合法分配未被提及的参与者，例如审查大师或文档专家；随后执行阶段因这些 Agent 不在调度列表中而失败。

### 完成内容
- 将非 mock planner 的 `participants` 和 `participant_ids` 限制到 `job["agents"]`；无提及时行为不变，因为调度解析已把无提及任务扩展到所有会话参与者。
- 保留完整 `availableAgentCatalog`，用于能力缺口推荐。
- 增加回归测试，覆盖较大群聊中的显式提及子集。
- 创建 mention-scoped planner 的 plan/checklist。

### 新增/修改文件
- `backend/app/ws/handlers.py`
- `backend/tests/test_m3_websocket_interactions.py`
- `docs/plans/M5_MENTION_SCOPED_PLANNER_PLAN.md`
- `docs/plans/M5_MENTION_SCOPED_PLANNER_CHECKLIST.md`
- `DEVLOG.md`

### 接口变更
- 无 API、WebSocket payload、共享类型、前端、adapter 或依赖变化。

### 验证
- `cd backend && .venv/bin/python -m pytest tests/test_m3_websocket_interactions.py -k "planner_context_is_scoped or non_mock_job_uses_deepseek_planner_wrapper"` -> `2 项通过`，带有既有 Starlette/httpx 弃用警告.
- `cd backend && .venv/bin/python -m pytest tests/test_m3_websocket_interactions.py` -> `9 项通过`，带有既有 Starlette/httpx 弃用警告.

## [2026-06-08] Codex - 修复 CDN 静态预览 CSP

### 问题判断
- 用户测试的 `index.html` 是生成后的静态页面，不是 Vite 源码项目。
- 页面从 HTTPS CDN 加载 React、ReactDOM、Babel standalone、Google Fonts 和图片。
- 预览 CSP 只允许同源脚本和内联脚本，导致 CDN 运行时脚本被阻止，React 根节点保持空白。

### 完成内容
- 扩展 Preview CSP，允许 iframe 内使用 HTTPS 脚本、样式、字体、图片和连接。
- 为浏览器内运行 `type="text/babel"` 的 Babel standalone 生成页增加 `unsafe-eval`。
- 保留 `frame-ancestors 'self'` 和既有 iframe sandbox 边界。
- 增加后端回归测试，覆盖 CDN/Babel 静态预览页面。
- 更新 Preview API 文档和 Vite 预览 plan/checklist。

### 新增/修改文件
- `backend/app/services/preview_service.py`
- `backend/tests/test_m4_artifact_preview.py`
- `docs/API_SPEC.md`
- `docs/plans/M5_VITE_HTML_PREVIEW_FIX_PLAN.md`
- `docs/plans/M5_VITE_HTML_PREVIEW_FIX_CHECKLIST.md`
- `DEVLOG.md`

### 接口变更
- 无路由、payload、共享类型或依赖变化。
- Preview 响应 CSP 有意放宽，以支持 iframe 中渲染的生成页面。

### 验证
- `cd backend && .venv/bin/python -m pytest tests/test_m4_artifact_preview.py` -> `4 项通过`，带有既有 Starlette/httpx 弃用警告.
- `curl -s -D - http://127.0.0.1:8000/preview/4a5690e1-ea91-4abe-80db-1690dd431002/index.html -o /tmp/agenthub-preview.html` 返回 `200 OK`，并包含更新后的 CSP `script-src 'self' 'unsafe-inline' 'unsafe-eval' https:`.


## [2026-06-08] Codex - 刷新侧边栏 Nailaude 品牌

### 完成内容
- 将用户提供的 Nailaude logo 添加为前端公共资源。
- 将侧边栏头部 home 图标和 `AgentHub` 文本替换为 Nailaude logo 和 `Nailaude` 标签。
- 调整侧边栏头部品牌图片尺寸和裁剪样式。
- 更新浏览器页面标题和 favicon，使用 Nailaude 品牌。

### 新增/修改文件
- `frontend/index.html`
- `frontend/public/brand/nailaude_logo.png`
- `frontend/src/components/chat/ConversationList.tsx`
- `frontend/src/index.css`
- `docs/plans/M5_BRANDING_REFRESH_PLAN.md`
- `docs/plans/M5_BRANDING_REFRESH_CHECKLIST.md`
- `DEVLOG.md`

### 接口变更
- 无 API、WebSocket、共享类型、后端或依赖变化。

### 验证
- `cd frontend && npm run build` -> 通过。
- `rg -n "AgentHub|HomeFilled|brand-mark__icon" frontend/src/components/chat/ConversationList.tsx frontend/src/index.css` -> 无匹配。
- 浏览器检查 `http://127.0.0.1:5173/workspace` 确认 品牌文本 `Nailaude` 以及已加载的 1254x1254 logo，渲染尺寸为 34x34。
- 浏览器标签栏检查 `http://127.0.0.1:5173/workspace` 确认 标签标题 `Nailaude`, `document.title` 为 `Nailaude`，favicon 为 `/brand/nailaude_logo.png`。

## [2026-06-08] Codex - 使用 Nailaude 图片替换内置 Agent 头像

### 完成内容
- 将四张用户提供的内置 Agent 头像图片添加为前端公共资源。
- 更新内置 Agent 种子数据，使代码工匠、审查大师、文档专家、产品架构师返回稳定的图片头像 URL。
- 更新前端头像渲染，支持显示图片 URL，同时保留文本/emoji 自定义头像兜底。

### 新增/修改文件
- `backend/app/services/seed.py`
- `backend/tests/test_m1_1_api.py`
- `docs/API_SPEC.md`
- `docs/plans/M5_BUILTIN_AGENT_AVATARS_PLAN.md`
- `docs/plans/M5_BUILTIN_AGENT_AVATARS_CHECKLIST.md`
- `frontend/public/agent-avatars/code_craftsman.png`
- `frontend/public/agent-avatars/review_master.png`
- `frontend/public/agent-avatars/doc_specialist.png`
- `frontend/public/agent-avatars/product_architect.png`
- `frontend/src/components/common/AgentAvatar.tsx`
- `frontend/src/components/chat/ChatArea.tsx`
- `frontend/src/components/chat/ConversationList.tsx`
- `frontend/src/components/chat/MentionSelector.tsx`
- `frontend/src/components/chat/MessageBubble.tsx`
- `frontend/src/pages/AgentManage.tsx`
- `frontend/src/index.css`
- `DEVLOG.md`

### 接口变更
- 无共享类型或 payload 结构变化。
- 内置 `Agent.avatar` 现在使用公共图片路径，不再使用单字母文本头像。

### 验证
- `cd backend && .venv/bin/python -m pytest tests/test_m1_1_api.py -k "agents_are_seeded or seed_refreshes_existing_builtin_agent_prompts"` -> `2 项通过`，带有既有 Starlette/httpx 弃用警告.
- `cd frontend && npm run build` -> 通过。
- `curl http://127.0.0.1:8027/api/v1/agents` 烟测期间返回 预期的四个 `/agent-avatars/*.png` 内置头像路径。
- 浏览器检查 `http://127.0.0.1:5174/workspace` 确认四个内置 Agent 头像均以已加载图片形式渲染。

## [2026-06-08] Codex - 新增自定义 Agent 头像上传

### 完成内容
- 添加用户提供的默认自定义 Agent 头像，并将其作为创建 Agent 弹窗默认值。
- 将短文本头像输入替换为图片预览、上传按钮和恢复默认操作。
- 增加客户端方形图片缩放，将上传的自定义头像保存为 data URL，并把后端头像存储扩展为 `Text`。

### 新增/修改文件
- `backend/alembic/versions/f3c289e260e9_initial_schema.py`
- `backend/app/models/agent.py`
- `backend/tests/test_m1_1_api.py`
- `docs/API_SPEC.md`
- `docs/plans/M5_CUSTOM_AGENT_AVATAR_UPLOAD_PLAN.md`
- `docs/plans/M5_CUSTOM_AGENT_AVATAR_UPLOAD_CHECKLIST.md`
- `frontend/public/agent-avatars/default_custom_agent.png`
- `frontend/src/components/chat/AgentCreateModal.tsx`
- `frontend/src/components/common/AgentAvatar.tsx`
- `frontend/src/index.css`
- `DEVLOG.md`

### 接口变更
- 无共享类型或 REST 路由结构变化。
- 自定义 `Agent.avatar` 现在除文本、emoji 和公共图片路径外，也可包含缩放后的 `data:image/*` URL。

### 验证
- `cd backend && .venv/bin/python -m pytest tests/test_m1_1_api.py -k "create_custom_agent_persists_and_lists"` -> `1 项通过`，带有既有 Starlette/httpx 弃用警告.
- `cd frontend && npm run build` -> 通过。
- 浏览器检查 `http://127.0.0.1:5174/workspace` 确认 创建 Agent 弹窗默认预览使用 `/agent-avatars/default_custom_agent.png`，通过上传按钮暴露 `image/*` 文件输入，并保持原生文件输入在视觉上隐藏。
