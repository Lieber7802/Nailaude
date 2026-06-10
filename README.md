# nailaude

nailaude 是一个带着奶龙气质的 IM 式多智能体协作工作台。它把需求分析、代码生成、代码审查、文档整理和产物预览都放进一个清清爽爽的聊天空间里，让多个 AI 智能体像一个小队一样围着同一个项目向前推进。

你可以把 nailaude 理解成一只认真帮忙的奶龙项目搭子：会听你说想法，会把任务拆开，会叫不同智能体各展所长，也会把生成的代码、Diff、网页预览、Markdown 文档和运行日志乖乖摆到你面前。用户不需要在一堆工具窗口里来回跳，聊天流就是项目推进现场。

nailaude 不打算重做 Codex、OpenCode 或 Claude Code。它做的是把这些成熟 Agent 平台接到一个统一、可追踪、可预览的协作工作台里，让 AI 开发从“单次问答”变成“有队友、有产物、有上下文”的连续协作。

## 它会做什么

- **单聊 / 群聊协作**：可以和一个智能体单独聊，也可以拉起多个智能体一起完成一个任务。
- **任务编排**：Orchestrator 会把用户输入拆成 Dispatch Plan，安排任务依赖、执行批次、运行状态和最终汇总。
- **多 Agent 接入**：统一 `AgentAdapter` 抽象，接入 Mock、LLM、OpenCode、Codex 等执行平台。
- **流式消息**：FastAPI WebSocket 持续推送文本增量、任务状态、产物卡片、团队动态和完成事件。
- **产物卡片**：代码、文件、Diff、网页、Markdown 文档、日志和部署状态都能在聊天流里变成可查看的 Artifact。
- **右侧预览面板**：网页、代码、Diff 和 Markdown 可以直接在工作台里检查，不用切出去找文件。
- **团队上下文**：Team Board、Project State 和 Handoff Context 会帮智能体共享决策、进度和项目状态。
- **Mock-first 闭环**：保留 MockAdapter，没接外部平台时也能稳定演示、测试和回归。

## 奶龙味在哪里

nailaude 的主题来自奶龙，但它不是只贴一个可爱外壳。它希望把“亲近感”和“工程可靠性”放在一起：

- 对用户来说，它像一个不吵闹但很积极的 AI 项目伙伴。
- 对智能体来说，它提供清晰边界、共享上下文和可验证结果。
- 对开发者来说，它保留契约、测试、Mock 和 DEVLOG，让协作不靠玄学。

简单说，就是外表软乎乎，内里很能干。

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | React + Vite + TypeScript + Ant Design |
| 状态管理 | Zustand |
| 代码 / Diff 预览 | Monaco Editor + diff2html |
| 后端 | Python FastAPI |
| 数据库 | SQLite + SQLAlchemy 2.0 + Alembic |
| 实时通信 | FastAPI WebSocket |
| Agent 接入 | Mock / LLM / OpenCode / Codex Adapter |
| 类型契约 | `packages/shared/types.ts` |

## 项目结构

```text
.
├── frontend/                 # React SPA 工作台
│   └── src/
│       ├── components/       # chat / cards / preview / common UI
│       ├── hooks/            # WebSocket 与滚动等 hooks
│       ├── pages/            # Workspace / Agent 管理等页面
│       ├── services/         # API 与 WebSocket 客户端
│       └── stores/           # Zustand stores
├── backend/                  # FastAPI 后端
│   └── app/
│       ├── adapters/         # AgentAdapter 实现
│       ├── api/              # REST 路由
│       ├── models/           # SQLAlchemy ORM
│       ├── schemas/          # Pydantic schema
│       ├── services/         # Orchestrator / Artifact / Preview 等核心服务
│       └── ws/               # WebSocket 连接与消息处理
├── packages/shared/          # 前后端共享 TypeScript 类型契约
├── docs/                     # PRD、技术设计、API 规范、计划与交付文档
├── workspaces/               # 会话项目工作区
├── AGENTS.md                 # AI 编码助手协作规范
├── CONTRIBUTING.md           # 团队协作与提交规范
└── DEVLOG.md                 # AI 编码会话沉淀日志
```

## 快速开始

### 1. 准备环境

- Node.js 20+（建议使用当前 LTS）
- Python 3.11+
- npm
- SQLite
- 可选：OpenCode / Codex CLI，用于真实 Agent Adapter 联调

### 2. 安装依赖

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```bash
cd frontend
npm install
```

### 3. 初始化数据库

```bash
cd backend
source .venv/bin/activate
alembic upgrade head
```

默认 SQLite 数据库为 `backend/nailaude.db`。如果要换数据库，可以通过环境变量 `DATABASE_URL` 覆盖。

### 4. 启动工作台

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

```bash
cd frontend
npm run dev
```

默认地址：

- 前端工作台：`http://localhost:5173`
- 后端 API：`http://localhost:8000/api/v1`
- WebSocket：`ws://localhost:8000/ws/{conversation_id}`
- 预览服务：`http://localhost:8000/preview/{conversation_id}/*`

## 常用命令

```bash
# 后端测试
cd backend
source .venv/bin/activate
pytest -q
```

```bash
# 前端测试
cd frontend
npm test
```

```bash
# 前端构建
cd frontend
npm run build
```

```bash
# 搜索品牌名使用位置
rg -n "Nailaude|nailaude|NAILAUDE"
```

## 开发方式

nailaude 是可爱的，但开发流程不靠卖萌。项目采用契约优先、Mock-first、测试优先的协作方式：

1. 修改接口、WebSocket、Adapter 或共享类型前，先阅读 `docs/API_SPEC.md` 和 `packages/shared/types.ts`。
2. 模块化开发前，在 `docs/plans/` 创建或更新对应 plan/checklist。
3. 新行为优先补测试，再实现功能。
4. 保留 MockAdapter，确保无外部依赖时仍能完成演示和回归。
5. 每次 AI 编码会话结束时，在 `DEVLOG.md` 追加记录。

更完整的 AI 协作规则见 `AGENTS.md` 和 `docs/AI_WORKFLOW.md`。

## 关键接口与事件

- REST 统一返回 `ApiResponse<T>`，详见 `docs/API_SPEC.md`。
- 前端正常发送消息优先走 WebSocket `send_message`。
- 后端会推送 `text_delta`、`artifact`、`team_activity`、`orchestrator_status`、`message_done` 等事件。
- Artifact、Conversation、Message、Task、TeamBoard 等核心类型以 `packages/shared/types.ts` 为准。

## Adapter 配置说明

nailaude 的智能体角色与底层平台解耦：

- 用户看到的是 Agent 角色，例如需求分析师、代码工匠、审查大师、文档专家。
- 后端根据角色绑定和平台健康状态选择 Mock、LLM、OpenCode 或 Codex Adapter。
- Codex Adapter 会使用隔离的 `CODEX_HOME` 和本地桥接令牌，避免读取或修改用户当前 Codex Desktop 配置。
- 相关环境变量使用 `NAILAUDE_` 前缀，例如 `NAILAUDE_CODEX_HOME_ROOT` 与 `NAILAUDE_CODEX_BRIDGE_TOKEN`。

## 交付文档

主要交付材料集中在：

- `docs/交付文档/PRODUCT_DESIGN.md`
- `docs/交付文档/TECHNICAL_DOCUMENT.md`
- `docs/交付文档/AI_COLLABORATION_PROCESS.md`

项目设计、API、任务拆解与技术债记录集中在 `docs/` 目录。需要回看产品设定、技术方案或 AI 协作过程时，从这里进就很顺手。
