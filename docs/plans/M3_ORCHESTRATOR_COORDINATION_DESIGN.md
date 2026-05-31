# M3 Orchestrator 协作上下文与状态设计

> 版本：v1.0
> 状态：已确认，作为 M3 组长侧后续实现基线
> 日期：2026-05-31
> 关联任务：`3.8 上下文分层构建`、`3.9 Team Board 数据结构`、`3.10 Project State 维护`、`3.11 OrchestratorStatus 推送`
> Planner 设计：`docs/plans/M3_ORCHESTRATOR_PLANNER_DESIGN.md`

---

## 一、设计原则

AgentHub 不重复实现 Codex 和 OpenCode 已具备的源码探索与上下文工程能力。

Orchestrator 只补充 CLI Agent 无法天然获取的协作信息：

```text
任务边界
+ 验收标准
+ 访问权限
+ 团队共享决策
+ 前序任务结果
+ 批次快照
+ 导航建议
```

原 PRD 中的四层上下文保留为解释性架构映射，不再实现重型源码筛选、全文注入和压缩引擎。

---

## 二、总体架构

```text
用户请求
→ PlannerContext
→ DeepSeek Planner
→ Task Contract
→ AgentHandoffEnvelope Builder
→ Codex / OpenCode CLI 自主探索受限工作目录

Project State ─┐
               ├→ PlannerContext / AgentHandoffEnvelope
Team Board ────┘

执行器
→ OrchestratorStatus 完整快照
→ WebSocket
→ 前端运行状态、问题卡片、审批卡片和聊天流
```

核心结构只有两个：

| 结构 | 用途 |
|---|---|
| `PlannerContext` | 让 Planner 理解用户目标并生成任务计划 |
| `AgentHandoffEnvelope` | 将单个任务可靠交接给 Codex、OpenCode 或其他 Adapter |

---

## 三、PlannerContext

Planner 只获得足够完成任务拆解的信息，默认不读取源码全文。

```json
{
  "userRequest": "...",
  "mentions": [],
  "clarificationAnswers": [],
  "participants": [],
  "availableAgentCatalog": [],
  "projectPlanningSummary": {},
  "teamBoardSummary": {},
  "recentConversationSummary": [],
  "fileTreeSummary": [],
  "previousValidationErrors": []
}
```

`availableAgentCatalog` 不包含底层 `platformId`。

---

## 四、AgentHandoffEnvelope

每个子任务启动前独立构建：

```json
{
  "runId": "run-123",
  "taskId": "task-2",
  "batchId": "batch-1",
  "workspace": {
    "path": "D:/workspaces/snapshot-abc",
    "accessMode": "read",
    "snapshotId": "snapshot-abc"
  },
  "task": {
    "title": "审查登录页",
    "objective": "检查新增登录页和鉴权服务集成。",
    "instruction": "输出明确的问题、原因和修复建议。",
    "acceptanceCriteria": [
      "检查失败状态处理",
      "检查敏感信息泄漏"
    ],
    "constraints": [
      "只读分析，不修改真实项目"
    ]
  },
  "collaboration": {
    "projectSummary": "...",
    "teamStandards": [],
    "relevantTeamNotes": [],
    "dependencyResults": []
  },
  "navigationHints": {
    "inspectFirst": [
      "src/pages/Login.tsx",
      "src/services/auth.ts"
    ],
    "changedFiles": [
      "src/pages/Login.tsx"
    ],
    "diffSummary": "新增登录提交、加载状态和错误提示。"
  },
  "manifest": {
    "estimatedTokens": 5400,
    "warnings": [],
    "omittedItems": []
  }
}
```

### CLI Agent 策略

- Codex 和 OpenCode 默认不注入源码全文。
- CLI Agent 可在受限工作目录内自主读取任意非敏感文件。
- `navigationHints` 只是效率建议，不是文件白名单。
- CLI Agent 记录实际读取和修改的文件列表。
- 前序任务默认只传递摘要、变更文件、Diff 摘要和 Team Notes。

### Envelope 预算

| 项目 | 限制 |
|---|---:|
| 软目标 | `16K tokens` |
| 硬上限 | `32K tokens` |
| Team Notes | 最多 `20` 条相关记录 |
| 依赖任务摘要 | 最多 `16` 条 |
| 最近聊天摘要 | 最多 `20` 条 |
| 源码全文 | CLI Agent 默认不注入 |

超出预算时，优先压缩或移除低相关历史、Team Notes、依赖摘要和低优先级导航建议。任务契约、权限和安全规则不得删除。

### 纯 API Adapter

纯 API 型 `LLMProviderAdapter` 没有文件工具，因此单独提供可选 `ContentMaterializer`：

```text
navigationHints
→ 读取少量必要文件
→ 敏感文件过滤
→ 控制预算
→ 超限时截断或摘要
→ 注入 API 请求
```

`ContentMaterializer` 不属于 Codex/OpenCode 默认路径，也不阻塞 M3 CLI Agent 主线。

---

## 五、并行快照策略

```text
Batch 开始
→ 创建统一快照 S0
├── write 任务：在真实 workDir 中运行
└── read 任务：各自在 S0 的独立临时副本中运行
→ 等待本批全部任务完成
→ 丢弃 read 临时副本
→ 合并任务结果和 Team Notes
→ 刷新 Project State 和 Team Board
→ 启动下一批
```

约束：

- 每批最多 `3` 个任务。
- 每批最多 `1` 个 `write`。
- 同批只读任务不会看到写任务的中间结果。
- 需要审查本批新增代码的任务必须进入后续批次。
- `read` 任务产生的意外修改全部丢弃。

---

## 六、Team Board 定位

Team Board 是每个会话的紧凑型协作快照，保存所有 Agent 都需要理解的团队状态：

```text
团队成员
+ 团队决策
+ 代码规范
+ 未解决问题
+ 协调进度
+ 最近 Team Notes
```

Team Board 不保存文件树、完整代码、Agent 日志或 Git 元数据。

---

## 七、Team Board 数据结构

```ts
interface TeamBoard {
  conversationId: UUID;
  version: number;
  teamMembers: TeamMember[];
  decisions: TeamDecision[];
  codeStandards: CodeStandard[];
  openQuestions: TeamQuestion[];
  progress: TeamProgress;
  recentNotes: TeamNote[];
  updatedAt: Timestamp;
}
```

```ts
interface TeamMember {
  agentId: UUID;
  name: string;
  role: string;
  capabilities: string[];
}
```

成员来自会话参与者，由后端自动同步。底层 `platformId` 不暴露。

```ts
interface TeamDecision {
  id: UUID;
  content: string;
  rationale: string;
  madeByAgentId: UUID;
  madeByAgentName: string;
  sourceTaskId: string;
  status: "active" | "review_required" | "superseded";
  supersedesDecisionId?: UUID;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}
```

```ts
interface CodeStandard {
  id: UUID;
  category: "naming" | "structure" | "style" | "testing" | "security" | "other";
  content: string;
  sourceTaskId: string;
  status: "active" | "review_required" | "superseded";
  supersedesStandardId?: UUID;
  updatedAt: Timestamp;
}
```

```ts
interface TeamProgress {
  completedTaskIds: string[];
  activeTaskIds: string[];
  blockedTaskIds: string[];
  pendingTaskIds: string[];
  currentFocus: string;
}
```

Team Progress 记录协调进度。更高层的项目进展摘要归 Project State 管理。

---

## 八、Team Notes 原子记录

Team Board 使用“单个快照 + 独立原子 Notes 记录”的混合存储。

```ts
interface TeamNote {
  id: UUID;
  conversationId: UUID;
  sourceTaskId: string;
  fromAgentId: UUID;
  fromAgentName: string;
  to: { type: "all" } | { type: "agent"; agentId: UUID };
  type: "decision" | "standard" | "heads_up" | "question" | "answer";
  content: string;
  relatedFiles: string[];
  relatedTaskIds: string[];
  resolvesNoteId?: UUID;
  status: "active" | "resolved" | "superseded" | "archived";
  injectionCount: number;
  lastInjectedAt?: Timestamp;
  createdAt: Timestamp;
  resolvedAt?: Timestamp;
}
```

每个任务最多接受 `10` 条 Notes，单条建议不超过 `1000` 字符。

### 生命周期

```text
created
→ active
├──→ resolved
├──→ superseded
└──→ archived
```

| Note 类型 | 生命周期 |
|---|---|
| `decision` | 保存后提升为 Team Decision；原 Note 保留用于审计 |
| `standard` | 保存后提升为 Code Standard |
| `heads_up` | 保持 active，解决后归档 |
| `question` | 保持 active，等待 answer |
| `answer` | 必须引用 `resolvesNoteId`，用于关闭 question |

Notes 注入后不自动消费，允许多次投递。

### 注入排序

构建 `AgentHandoffEnvelope` 时，最多选择 `20` 条 Notes：

```text
目标为当前 Agent 的 Notes
→ 目标为 all 的 Notes
→ 来自直接依赖任务的 Notes
→ relatedFiles 与导航路径重合的 Notes
→ 最近创建的 Notes
```

注入后更新 `injectionCount` 和 `lastInjectedAt`。

---

## 九、Team Board 批次合并

并行 Agent 不得直接修改 Team Board。所有结果在批次屏障统一合并：

```text
Batch 完成
→ 收集 TaskResult 和 Team Notes
→ 校验和原子化
→ 去重
→ 保存 Notes
→ 生成 Board Patch
→ 校验 Patch
→ 更新 Team Board version
→ 推送 team_activity 和 team_board_updated
```

### 确定性规则

| 场景 | 行为 |
|---|---|
| 重复 Note | 根据类型、目标、标准化内容、相关文件生成指纹，只保留一条 |
| 成功任务 | 接受全部合法 Notes |
| 部分成功任务 | 接受 `heads_up`、`question`；decision 和 standard 标记 `review_required` |
| 失败任务 | 仅接受 `heads_up`、`question` |
| 新增决策 | 无冲突时自动变为 `active` |
| 替换旧决策 | 旧项标记 `superseded`，保留历史 |
| 无法判断冲突 | 标记 `review_required`，不得静默覆盖 |
| Progress | 根据执行器真实任务状态更新，不由 LLM 猜测 |

### Board Summarizer

DeepSeek 可在批次结束时提出紧凑 `BoardPatch`：

```json
{
  "addDecisions": [],
  "supersedeDecisions": [],
  "addStandards": [],
  "supersedeStandards": [],
  "resolveQuestions": [],
  "currentFocus": "登录页集成审查"
}
```

LLM 只提出 Patch。后端验证引用 ID、来源任务和状态迁移。LLM 失败时不阻塞后续批次：Notes 仍保存，Progress 仍按确定性规则更新。

---

## 十、Project State 定位

Project State 是工作目录的事实快照和紧凑摘要：

```text
Python 确定性扫描事实
+ Git 元数据
+ DeepSeek 增量摘要
```

Project State 不替代 Git，不保存源码全文，也不重复保存 Team Board 的决策和规范。

---

## 十一、Project State 数据结构

```ts
interface ProjectState {
  conversationId: UUID;
  version: number;
  workspace: {
    name: string;
    workDir: string;
    scannedAt: Timestamp;
    fingerprint: string;
  };
  techStack: string[];
  fileTree: {
    totalFiles: number;
    paths: string[];
    truncated: boolean;
  };
  git: {
    isRepository: boolean;
    branch?: string;
    headCommit?: string;
    dirty: boolean;
    recentCommits: Array<{ sha: string; message: string }>;
  };
  progressSummary: string;
  recentChanges: ProjectChange[];
  updatedAt: Timestamp;
}
```

```ts
interface ProjectChange {
  file: string;
  changeType: "created" | "modified" | "deleted" | "renamed";
  summary: string;
  source: "agent" | "external";
  agentId?: UUID;
  taskId?: string;
  batchId?: string;
  createdAt: Timestamp;
}
```

---

## 十二、Project State 更新

| 时机 | 操作 |
|---|---|
| 首次打开会话或首次规划 | 初始化扫描 |
| Planner 运行前 | 轻量扫描，检测外部修改 |
| 每个 Batch 开始 | 冻结当前 Project State version |
| 每个 Batch 结束 | 完整刷新，记录 Agent 变更 |
| 用户手动刷新 | 重新扫描 |

同批任务共享同一个版本，避免并行任务看到不同状态。

### WorkspaceScanner

```text
扫描安全相对路径
→ 过滤敏感目录和文件
→ 收集路径、大小、mtime
→ 计算 fingerprint
→ 限制最大文件数量
```

默认：

- 存储完整安全路径列表最多 `5000` 条。
- PlannerContext 只注入最多 `500` 条代表性路径。
- 超过限制时标记 `truncated: true`。

### GitInspector

```text
判断是否为 Git 仓库
→ 获取 branch 和 HEAD
→ 读取最近 5 条 commit
→ 读取 status --short
→ 读取 diff --stat
```

Git 命令设置短超时，例如 `3s`。非 Git 目录正常降级，不阻塞执行。

### 增量摘要

DeepSeek 只在检测到变更时生成摘要，不读取整个仓库：

```text
旧 progressSummary
+ 文件树差异
+ Git diff --stat
+ TaskResult.summary
+ filesChanged
→ Project State Summarizer
→ 新 progressSummary + recentChanges 摘要
```

LLM 摘要失败时保留旧摘要，保存确定性扫描结果并记录 warning，不阻塞后续任务。

---

## 十三、安全文件过滤与审计

默认禁止读取、主动注入或越权访问：

```text
.env
.env.*
*.pem
*.key
*.p12
*.pfx
id_rsa*
credentials*
secrets*
.git/
node_modules/
缓存目录
构建目录
workDir 外路径
软链接跳出 workDir 的目标
```

允许读取 `.env.example`。

Adapter 执行后返回：

```json
{
  "filesRead": [],
  "filesChanged": [],
  "filesCreated": [],
  "filesDeleted": [],
  "warnings": []
}
```

删除或重命名任意文件、修改配置文件、预计影响超过 `10` 个文件时，需要用户确认。

---

## 十四、Team Board 与 Project State API

M3 对前端只开放读取：

```text
GET /api/v1/conversations/{id}/team-board
GET /api/v1/conversations/{id}/project-state
```

写入仅由内部服务执行，避免前端直接篡改共享状态。

---

## 十五、OrchestratorStatus 定位

OrchestratorStatus 负责向前端实时展示：

- Planner 当前阶段。
- 是否正在等待用户回答或确认。
- 当前执行到第几个批次。
- 每个任务由谁负责、状态如何。
- 是否存在失败或阻塞。
- Team Board 和 Project State 是否已刷新。

每次发送完整快照，不使用增量 Patch。

---

## 十六、OrchestratorStatus 数据结构

```ts
type OrchestratorRunStatus =
  | "queued"
  | "planning"
  | "awaiting_input"
  | "validating"
  | "replanning"
  | "awaiting_approval"
  | "executing"
  | "summarizing"
  | "completed"
  | "failed"
  | "cancelled";
```

```ts
type TaskStatus =
  | "pending"
  | "ready"
  | "running"
  | "completed"
  | "failed"
  | "blocked"
  | "cancelled";
```

```ts
type BatchStatus =
  | "pending"
  | "running"
  | "completed"
  | "partial"
  | "failed"
  | "cancelled";
```

完整快照：

```json
{
  "type": "orchestrator_status",
  "data": {
    "runId": "run-123",
    "sequence": 12,
    "status": "executing",
    "message": "正在执行第 1 / 3 批任务",
    "reasoningSummary": "实现与现有风险分析可以并行。",
    "currentBatchIndex": 0,
    "totalBatches": 3,
    "tasks": [],
    "batches": [],
    "warnings": [],
    "teamBoardVersion": 4,
    "projectStateVersion": 7,
    "createdAt": "...",
    "updatedAt": "..."
  }
}
```

`sequence` 在同一 run 内单调递增。前端忽略更旧的快照，避免并行推送乱序覆盖新状态。

聊天流展示 Planner 的简短 `reasoningSummary` 和批次安排，不展示模型完整思维过程。

---

## 十七、状态推送时机

| 时机 | Run 状态 |
|---|---|
| 用户消息进入队列 | `queued` |
| 调用 Planner | `planning` |
| Planner 请求用户补充或推荐 Agent | `awaiting_input` |
| 规则层校验计划 | `validating` |
| 首次非法计划自动重规划 | `replanning` |
| 高风险写任务等待确认 | `awaiting_approval` |
| 任一批次正在运行 | `executing` |
| 所有任务结束，刷新共享状态 | `summarizing` |
| 执行和必要刷新结束 | `completed` |
| 无法继续 | `failed` |
| 用户停止生成 | `cancelled` |

任务执行成功但 Team Board 或 Project State 刷新失败时，Run 仍算 `completed`，但附带 warning。

---

## 十八、消息队列

同一会话同时只允许一个活跃 Orchestrator Run。

已有 Run 执行时，用户再次发送消息：

```text
新消息正常持久化
→ 创建 queued run
→ 推送 queued 状态和队列位置
→ 当前 run 结束后自动启动下一条
```

建议初始限制：

- 队列按消息创建时间 FIFO。
- 每个会话最多排队 `10` 条消息。
- 超过上限时拒绝新 Run，并推送 recoverable error。
- `stop_generation` 默认取消当前整个 Run，不自动清空后续队列。
- 被取消 Run 的下游任务标记为 `cancelled`。

---

## 十九、失败、取消与重连

### 任务失败

- 单个任务失败时，与它无依赖关系的任务继续执行。
- 依赖失败任务的下游任务标记为 `blocked`。
- 批次根据结果标记为 `partial` 或 `failed`。

### 用户取消

- `stop_generation` 取消整个当前 Run。
- 后端尽力终止正在执行的 Agent。
- 已完成任务结果保留。
- 未开始任务标记为 `cancelled`。

### 断线重连

- 服务器保留当前 Run 最新完整快照。
- 客户端重连后立即接收最新快照。
- 前端根据 `sequence` 忽略更旧状态。

---

## 二十、额外交互事件

状态快照之外，单独推送需要用户处理的事件：

```text
orchestrator_input_required
  clarification | capability_gap

orchestrator_input_response
  answers | approvedAgentIds

orchestrator_approval_required
  elevated_write_operation

orchestrator_approval_response
  approved | rejected

team_board_updated
project_state_updated
```

---

## 二十一、实现阶段契约变更

实现时需要同步修改 `packages/shared/types.ts` 和 `docs/API_SPEC.md`：

- 新增 `PlannerContext`、`AgentHandoffEnvelope`、`TaskResult` 文件审计字段。
- `TeamNote` 改为独立原子记录。
- `TeamDecision` 增加 ID、来源和状态。
- `codeStandards` 从字典调整为对象数组。
- `TeamBoard` 增加 `version`、`openQuestions`、`recentNotes`。
- `ProjectState` 增加 `workspace`、`git`、`version` 和结构化文件树。
- `TaskStatus` 增加 `ready`、`blocked`、`cancelled`。
- 新增 `BatchStatus` 和 `OrchestratorRunStatus`。
- 扩展 `orchestrator_status` 完整快照。
- 新增规划问题、Agent 推荐、风险确认、共享状态刷新 WS 消息。

---

## 二十二、已确认决策

- 不实现重型四层上下文引擎。
- 使用 `PlannerContext + AgentHandoffEnvelope`。
- CLI Agent 自主探索受限目录内的非敏感文件。
- `navigationHints` 仅作为建议。
- 前序任务默认只传递摘要、变更文件、Diff 摘要和 Team Notes。
- `ContentMaterializer` 仅用于纯 API Adapter。
- Handoff Envelope 采用 `16K` 软目标和 `32K` 硬上限。
- Team Board 使用“单个快照 + 独立原子 Notes 记录”。
- 并行任务只提交 Notes，由批次屏障统一合并。
- Board Summarizer 仅提出 Patch，失败不阻塞执行。
- 冲突决策标记为 `review_required`，不得静默覆盖。
- Notes 注入后不自动消费，允许多次投递。
- Project State 只保存项目事实和摘要。
- Project State 使用 Python 扫描、Git Inspector 和 DeepSeek 增量摘要。
- 安全文件树最多存储 `5000` 条路径，Planner 默认最多接收 `500` 条代表性路径。
- Team Board 和 Project State 对前端只开放 GET API。
- OrchestratorStatus 每次发送完整快照。
- 同一会话同时只运行一个活跃 Run，新消息进入 FIFO 队列。
- `stop_generation` 取消整个当前 Run。
- 单个任务失败时，无依赖任务继续执行。
- 共享状态刷新失败时 Run 仍为 `completed`，但附带 warning。
- 断线重连后立即推送当前 Run 最新完整快照。
- 聊天流展示 Planner 的简短 `reasoningSummary` 和批次安排。
