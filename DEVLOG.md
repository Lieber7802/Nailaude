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
