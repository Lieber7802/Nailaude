# AGENTS.md — AI 编码助手协作指南

> 本文档指导 Claude Code、Codex、OpenCode 等 AI 编码助手参与 AgentHub 项目开发。  
> 修改代码前请先阅读本文件。

---

## 项目目标

AgentHub 是一个 **IM 式多 Agent 协作工作台**（20 天比赛 MVP）：

- 用户通过聊天界面与多个 AI Agent 交互（单聊 / 群聊）
- Orchestrator 自动拆解任务、分派给不同 Agent、汇总结果
- Agent 产出以产物卡片（代码 / Diff / 网页预览）内联展示在聊天流中
- 统一 Agent Adapter 层接入 OpenCode、Codex 等第三方 Agent 平台
- Team Protocol 让 Agent 间共享决策和上下文

## 项目不是

- ❌ 不是自研 Claude Code / Codex（我们接入它们，不复刻它们）
- ❌ 不是复杂企业级 Agent Framework（MVP 够用即可）
- ❌ 不优先做 P2 功能（部署、移动端、PPT 预览等暂不实现）
- ❌ 不是普通多模型聊天窗口（强调协作、产物、Diff）

---

## 技术栈

| 层 | 技术 | 说明 |
|---|------|------|
| 前端 | React 18 + Vite + TypeScript | 纯 SPA，Ant Design 组件库 |
| 状态管理 | Zustand | 轻量，无 boilerplate |
| 代码编辑器 | Monaco Editor | Diff 视图 + 语法高亮 |
| 后端 | Python FastAPI | 异步，WebSocket 原生支持 |
| 数据库 | SQLite + SQLAlchemy 2.0 | 开发环境，可切 PostgreSQL |
| 实时通信 | WebSocket（FastAPI 原生） | 流式消息推送 |
| Agent 接入 | AgentAdapter 抽象层 | Mock / LLM / OpenCode / Codex |
| 共享类型 | packages/shared/types.ts | 前后端共享的 TypeScript 类型契约 |

---

## 目录结构

```
AgentHub/
├── AGENTS.md                 ← 你正在读的文件
├── frontend/                 # React SPA
│   └── src/
│       ├── pages/            # 页面组件
│       ├── components/       # UI 组件（chat/ cards/ preview/ common/）
│       ├── stores/           # Zustand store
│       ├── services/         # API + WebSocket 客户端
│       └── hooks/            # 自定义 Hooks
├── backend/                  # Python FastAPI
│   └── app/
│       ├── api/              # REST 路由
│       ├── ws/               # WebSocket 处理
│       ├── services/         # 业务逻辑（orchestrator, agent_manager, etc.）
│       ├── adapters/         # Agent 适配器（mock, llm_provider, opencode, codex）
│       ├── models/           # SQLAlchemy ORM 模型
│       └── schemas/          # Pydantic 请求/响应 schema
├── packages/shared/          # 共享类型
│   └── types.ts              # 前后端共享的 TypeScript 类型定义（核心契约）
├── docs/                     # 文档
│   ├── PRD.md                # 产品需求文档
│   ├── TECH_DESIGN.md        # 技术设计文档
│   ├── API_SPEC.md           # API 规范
│   └── TASK_BREAKDOWN.md     # 任务拆解与分工
└── workspaces/               # Agent 工作目录（用户项目文件存放于此）
```

### 模块边界规则

| 模块 | 职责 | 不应该做的 |
|------|------|-----------|
| `frontend/` | UI 渲染、用户交互、WebSocket 客户端 | 不直接调用 Agent、不处理文件系统 |
| `backend/api/` | HTTP 路由、参数校验 | 不含业务逻辑，只调用 services |
| `backend/services/` | 核心业务逻辑 | 不直接操作数据库（通过 models） |
| `backend/adapters/` | Agent 平台接入 | 不知道具体业务场景，只实现 `run_task()` |
| `packages/shared/` | 类型契约 | 不含任何运行时代码或业务逻辑 |
| `docs/` | 规范文档 | 不含代码实现 |

---

## 核心概念

| 概念 | 说明 | 对应类型 |
|------|------|---------|
| **Agent** | 用户看到的 AI 角色（"代码工匠"），绑定到某个底层平台 | `Agent` |
| **AgentPlatform** | 底层执行平台（mock/llm/opencode/codex），用户不可见 | `AgentPlatform` |
| **Conversation** | 聊天会话（单聊/群聊），绑定项目目录 | `Conversation` |
| **Message** | 一条聊天消息（用户/Agent/Orchestrator/Team Activity） | `Message` |
| **Artifact** | Agent 产出的产物（代码/Diff/网页/文件/日志） | `Artifact` |
| **Orchestrator** | 群聊中的任务调度器，拆解意图、分派 Agent、汇总结果 | `DispatchPlan`, `Task` |
| **AgentAdapter** | Agent 平台适配器抽象，核心接口是 `run_task()` | `AgentInput`, `AgentOutput`, `AgentEvent` |
| **TeamBoard** | Agent 间共享的团队看板（决策/规范/进度） | `TeamBoard`, `TeamNote` |
| **SkillRule** | 自动触发规则（如"生成代码后自动审查"） | `SkillRule` |

---

## AI 编码规则

### 标准模块化流程

后续所有模块化开发（M 系列任务、后端/前端功能、WebSocket、Adapter、Artifact、预览系统）统一采用：

`接收任务 → 读取契约 → 生成/更新 plan 和 checklist → 测试先行 → 按 plan 实现 → 运行验证 → 更新 DEVLOG → 总结交接`

详细流程见 `docs/AI_WORKFLOW.md`。如果当前 AI 环境支持项目 skill，应使用 `.agents/skills/agenthub-module-development/SKILL.md`。

### 修改前

1. **先读文档**：修改前阅读 `docs/API_SPEC.md` 和 `packages/shared/types.ts`，确认接口契约
2. **先说计划**：在写代码前说明你打算改哪些文件、为什么改、预期效果
3. **确认范围**：只改和当前任务相关的文件，不"顺手"重构无关代码
4. **先沉淀计划**：模块化开发需在 `docs/plans/` 下创建或更新 `<MODULE>_PLAN.md` 和 `<MODULE>_CHECKLIST.md`

### 修改中

5. **不随意改 shared types**：`packages/shared/types.ts` 是全局契约，修改需同步更新 `API_SPEC.md`
6. **不随意引入新依赖**：新增 npm/pip 依赖前说明理由，评估包大小和必要性
7. **Mock-first**：实现新功能时先确保 MockAdapter 能覆盖该场景
8. **Test-first**：功能、修复、行为变化优先写失败测试，再写实现
9. **API 一致性**：后端接口的请求/响应格式必须与 `API_SPEC.md` 一致
10. **类型安全**：前端使用 `shared/types.ts` 中的类型，不重复定义

### 修改后

11. **总结改动**：列出修改了哪些文件、改动摘要
12. **说明测试方式**：如何验证改动正确（启动命令、请求示例、预期结果）
13. **沉淀 DEVLOG**：每次 AI 编码会话结束时追加 `DEVLOG.md`

### 禁止事项

- ❌ 不要修改 `.env` 中的 API Key 或凭据
- ❌ 不要删除 MockAdapter（它是永久组件）
- ❌ 不要在 adapters/ 中引入业务逻辑
- ❌ 不要把 `platformId` 暴露给前端用户界面
- ❌ 不要实现 P2 功能（除非被明确要求）

---

## 常见操作指南

### 如何新增 Agent Provider

1. 在 `backend/app/adapters/` 下创建新文件（如 `new_provider.py`）
2. 继承 `AgentAdapter`，实现 `run_task()` 和 `health_check()`
3. 参考 `mock.py` 的事件 yield 模式
4. 在 `PlatformId` 类型中新增标识（需同步 `types.ts`）
5. 在 `backend/app/services/agent_manager.py` 注册新 Adapter

```python
# 最小实现模板
class NewProviderAdapter(AgentAdapter):
    platform_name = "new_provider"

    async def health_check(self) -> bool:
        return True

    async def run_task(self, work_dir, instruction, context) -> AsyncGenerator[AgentEvent, None]:
        # 你的逻辑
        yield AgentEvent(type="text_delta", content="Hello")
        yield AgentEvent(type="done", content="")
```

### 如何新增 Artifact 类型

1. 在 `packages/shared/types.ts` 的 `ArtifactType` 联合类型中新增值
2. 在 `docs/API_SPEC.md` 补充该类型的 artifact 推送示例
3. 后端：在 `backend/app/services/artifact_service.py` 中处理新类型的生成逻辑
4. 前端：在 `frontend/src/components/cards/` 下新增对应的卡片组件
5. 前端：在 MessageBubble 中注册新卡片的渲染分支

### 如何处理 WebSocket 消息

**后端推送新消息类型：**
1. 在 `types.ts` 的 `WSServerMessage` 联合类型中新增分支
2. 在 `backend/app/ws/handlers.py` 中添加推送逻辑
3. 前端 `useWebSocket` hook 中添加对应 case 分支

**前端接收示例：**
```typescript
// src/hooks/useWebSocket.ts 中的 switch
case 'text_delta':
  messageStore.appendStreamDelta(msg.data.messageId, msg.data.delta);
  break;
case 'artifact':
  artifactStore.addArtifact(msg.data.messageId, msg.data.artifact);
  break;
// 新增类型在此添加 case
```

### 如何验证改动

| 层 | 验证方式 |
|---|---------|
| 后端 API | `curl` 或 HTTPie 直接调用，对照 API_SPEC 检查响应格式 |
| WebSocket | 浏览器 DevTools → Network → WS tab 观察消息流 |
| 前端组件 | 启动 dev server，用 MockAdapter 触发对应事件，检查 UI 渲染 |
| Agent Adapter | 单独运行 adapter 的 `run_task()`，打印 event 流 |
| 全链路 | 发消息 → 观察 WS 推送 → 检查消息流 + 卡片 + 预览 |

```bash
# 快速启动
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev  # → http://localhost:5173
```

---

## 关键文件速查

| 需求 | 文件 |
|------|------|
| 查看所有类型定义 | `packages/shared/types.ts` |
| 查看 API 契约 | `docs/API_SPEC.md` |
| 查看 Adapter 接口 | `backend/app/adapters/base.py` |
| 查看 Mock 参考实现 | `backend/app/adapters/mock.py` |
| 查看 Orchestrator 逻辑 | `backend/app/services/orchestrator.py` |
| 查看前端状态管理 | `frontend/src/stores/` |
| 查看 WebSocket 处理 | `frontend/src/hooks/useWebSocket.ts` |
| 查看产品需求 | `docs/PRD.md` |
| 查看技术架构 | `docs/TECH_DESIGN.md` |
| 查看任务分工 | `docs/TASK_BREAKDOWN.md` |

---

## 命名约定

| 类别 | 约定 | 示例 |
|------|------|------|
| 前端组件 | PascalCase | `ChatArea.tsx`, `CodeCard.tsx` |
| 前端 store | camelCase + Store | `messageStore.ts` |
| 后端 API 路由 | snake_case | `conversations.py` |
| 后端 service | snake_case + Service | `orchestrator.py` |
| 后端 adapter | snake_case + Adapter | `opencode.py` |
| 数据库表名 | 复数 snake_case | `conversations`, `messages` |
| TypeScript 类型 | PascalCase | `Conversation`, `AgentEvent` |
| Python 类 | PascalCase | `AgentAdapter`, `MockAdapter` |
| Python 函数 | snake_case | `run_task`, `send_message` |
