# AgentHub AI 模块化开发标准流程

> 本流程用于 AgentHub 后续所有模块化开发：M 系列里程碑、后端/前端功能、WebSocket、Adapter、Artifact、预览系统和测试补齐。

## 核心原则

- **Contract-first**：先读 `docs/API_SPEC.md` 和 `packages/shared/types.ts`，再改 API、WS、前端服务或 Adapter。
- **Plan-first**：先沉淀计划和 checklist，再实现。
- **Mock-first**：真实 Agent 接入前，必须保证 MockAdapter 能覆盖对应场景。
- **Test-first**：功能、修复、行为变化先写失败测试，再写实现。
- **Verification-first**：没有新鲜测试或烟测结果，不声称完成。
- **DEVLOG-first handoff**：每次 AI 编码会话结束，都在 `DEVLOG.md` 追加简短记录。

## 标准流程

### 1. 接收任务

- 明确任务属于哪个阶段或模块，例如 `M1_2`、`M4 PreviewPanel`、`AgentAdapter`。
- 明确本次目标、输入、输出和不做什么。
- 如果任务会影响共享契约，提前标记为契约变更。

### 2. 读取上下文

必读：

- `AGENTS.md`
- `docs/API_SPEC.md`
- `packages/shared/types.ts`
- `docs/TASK_BREAKDOWN.md`
- 当前模块相关的 `docs/plans/*`

按需阅读：

- `docs/PRD.md`
- `docs/TECH_DESIGN.md`
- 相关实现文件和测试文件

### 3. 生成或更新计划

在 `docs/plans/` 下创建或更新：

- `<MODULE>_PLAN.md`
- `<MODULE>_CHECKLIST.md`

计划至少包含：

- 目标
- 范围和非范围
- 契约影响
- 实现步骤
- 测试方式
- 验收标准

Checklist 要可勾选、可验证，避免“完善错误处理”这类不可验收描述。

### 4. 按计划实现

- 先写失败测试并确认失败原因正确。
- 按 checklist 小步实现。
- API/WS 响应必须对齐 `API_SPEC.md`。
- 前端类型优先来自 `packages/shared/types.ts`。
- 后端 `api/` 只做路由、参数校验和调用 service。
- `services/` 放核心业务逻辑。
- `adapters/` 只实现 Agent 平台通信，不写业务判断。
- 新增依赖前说明原因和必要性。

### 5. 验证

根据修改范围选择验证：

| 范围 | 最低验证 |
|---|---|
| 后端 API | `cd backend && pytest -q`，必要时加 HTTP 冒烟 |
| WebSocket | WS 客户端或测试脚本观察事件流 |
| 前端 | `cd frontend && npm run build`，必要时浏览器截图/交互 |
| Shared types | 前后端相关测试或构建都要跑 |
| Artifact/Preview | 文件生成、Diff、iframe/静态资源访问验证 |

最终回复必须写明实际运行的命令和结果。

### 6. 沉淀交接

更新 `DEVLOG.md`，包含：

- 完成内容
- 新增/修改文件
- 是否修改契约文件
- 下一步
- 给其他成员的提醒

如果创建或更新了计划/checklist，也在 DEVLOG 中说明。

## 项目 Skill

本仓库提供项目本地 skill：

`/.agents/skills/agenthub-module-development/SKILL.md`

当任务涉及 AgentHub 模块开发、里程碑执行、后端/前端功能、Adapter、Artifact、WebSocket 或 checklist-driven work 时，AI 助手应优先使用该 skill。

## 推荐命名

计划文件：

- `docs/plans/M1_TOTAL_PLAN.md`
- `docs/plans/M1_2_PLAN.md`
- `docs/plans/M1_2_CHECKLIST.md`

分支：

- `codex/m1-2-websocket-mock-stream`
- `feat/chat-message-flow`
- `fix/ws-reconnect`

提交：

```text
feat(module): concise summary

- Detail 1
- Detail 2

影响: backend/ws, frontend/hooks
关联: TASK_BREAKDOWN M1.2
```
