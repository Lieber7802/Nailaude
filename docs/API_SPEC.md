# AgentHub API 规范文档

> 版本：v1.1 | 基于 PRD v1.6 + TECH_DESIGN v1.1 + shared/types.ts  
> Base URL: `http://localhost:8000/api/v1`  
> WebSocket: `ws://localhost:8000/ws/{conversation_id}`  
> Preview: `http://localhost:8000/preview/{conversation_id}/*`（不经过 /api/v1）

---

## 一、通用约定

### 响应格式

所有 REST 接口统一返回 `ApiResponse<T>` 格式：

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "timestamp": "2026-05-21T10:30:00Z"
}
```

错误时：

```json
{
  "success": false,
  "data": null,
  "error": "Conversation not found",
  "timestamp": "2026-05-21T10:30:00Z"
}
```

### 分页

列表接口支持 `?page=1&pageSize=20`，返回 `PaginatedResponse<T>`。

### 消息发送方式

| 方式 | 路径 | 定位 |
|------|------|------|
| **WebSocket（首选）** | `ws://.../ws/{conversation_id}` 发送 `send_message` | 生产主路径，支持流式推送 |
| REST（备选） | `POST /api/v1/conversations/{id}/messages` | Fallback / 调试 / WS 不可用时 |

> 前端正常流程**优先走 WebSocket 发送消息**。REST 接口作为降级和调试入口保留。

---

## 二、Conversation API

### `POST /conversations` — 创建会话

**用途：** 新建单聊或群聊会话。

请求体：
```json
{
  "title": "Todo App 开发",
  "type": "group",
  "workDir": "/home/user/projects/todo-app",
  "participantIds": ["agent-uuid-1", "agent-uuid-2"]
}
```

响应体：
```json
{
  "success": true,
  "data": {
    "id": "conv-uuid-123",
    "title": "Todo App 开发",
    "type": "group",
    "workDir": "/home/user/projects/todo-app",
    "participantIds": ["agent-uuid-1", "agent-uuid-2"],
    "participants": [
      { "id": "agent-uuid-1", "name": "代码工匠", "avatar": "🛠️" },
      { "id": "agent-uuid-2", "name": "审查大师", "avatar": "🔍" }
    ],
    "createdBy": "user-uuid",
    "createdAt": "2026-05-21T10:30:00Z",
    "updatedAt": "2026-05-21T10:30:00Z"
  },
  "error": null,
  "timestamp": "2026-05-21T10:30:00Z"
}
```

---

### `GET /conversations` — 获取会话列表

**用途：** 左栏展示所有会话，按最近活跃排序。

查询参数：`?page=1&pageSize=20&search=todo`

响应体：
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "conv-uuid-123",
        "title": "Todo App 开发",
        "type": "group",
        "workDir": "/home/user/projects/todo-app",
        "participantIds": ["agent-uuid-1", "agent-uuid-2"],
        "participants": [...],
        "createdAt": "2026-05-21T10:30:00Z",
        "updatedAt": "2026-05-21T11:00:00Z",
        "lastMessage": "代码工匠: 已完成 TodoList 组件..."
      }
    ],
    "total": 5,
    "page": 1,
    "pageSize": 20
  }
}
```

---

### `GET /conversations/{id}` — 获取会话详情

**用途：** 切换会话时加载详情（含参与 Agent 完整信息）。

---

### `DELETE /conversations/{id}` — 删除会话

---

## 三、Message API

### `POST /conversations/{id}/messages` — 发送消息（REST Fallback）

**用途：** 用户发送消息的 REST 备选接口。正常流程应优先走 WebSocket `send_message`。后端接收后触发 Orchestrator 分派 + Agent 调用，通过 WebSocket 推送流式结果。

请求体：
```json
{
  "content": "@代码工匠 帮我生成一个 Todo List 页面，@审查大师 检查代码质量",
  "mentions": [
    { "agentId": "agent-uuid-1", "agentName": "代码工匠" },
    { "agentId": "agent-uuid-2", "agentName": "审查大师" }
  ],
  "parentMessageId": null
}
```

响应体（仅确认接收，实际回复通过 WebSocket 推送）：
```json
{
  "success": true,
  "data": {
    "id": "msg-uuid-user-1",
    "conversationId": "conv-uuid-123",
    "role": "user",
    "agentId": null,
    "content": "@代码工匠 帮我生成一个 Todo List 页面...",
    "contentType": "text",
    "artifacts": [],
    "parentMessageId": null,
    "metadata": {},
    "createdAt": "2026-05-21T11:00:00Z"
  }
}
```

---

### `GET /conversations/{id}/messages` — 获取消息历史

**用途：** 进入会话时加载历史消息。

查询参数：`?page=1&pageSize=50`

响应体：
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "msg-uuid-1",
        "role": "user",
        "agentId": null,
        "content": "帮我生成一个登录页面",
        "contentType": "text",
        "artifacts": [],
        "createdAt": "2026-05-21T10:31:00Z"
      },
      {
        "id": "msg-uuid-2",
        "role": "agent",
        "agentId": "agent-uuid-1",
        "agentName": "代码工匠",
        "content": "好的，我来为你生成...",
        "contentType": "mixed",
        "artifacts": [
          {
            "id": "art-uuid-1",
            "type": "code",
            "title": "index.html",
            "files": [{ "name": "index.html", "content": "...", "language": "html" }],
            "diffData": null,
            "previewUrl": "/preview/conv-uuid-123/index.html",
            "version": 1
          }
        ],
        "createdAt": "2026-05-21T10:31:30Z"
      }
    ],
    "total": 12,
    "page": 1,
    "pageSize": 50
  }
}
```

---

### `POST /messages/{id}/regenerate` — 重新生成消息

**用途：** 重新触发 Agent 生成（P1 功能）。

响应：同发送消息，结果通过 WebSocket 推送。

---

## 四、Agent API

### `GET /agents` — 获取所有 Agent 角色

**用途：** 展示 Agent 列表/联系人、新建对话时选择 Agent。

响应体：
```json
{
  "success": true,
  "data": [
    {
      "id": "agent-uuid-1",
      "name": "代码工匠",
      "avatar": "🛠️",
      "description": "全栈开发专家，擅长生成 React/HTML/CSS 代码",
      "capabilities": ["代码生成", "前端", "全栈"],
      "systemInstruction": "...",
      "platformId": "opencode",
      "isBuiltin": true,
      "createdAt": "2026-05-20T00:00:00Z"
    },
    {
      "id": "agent-uuid-2",
      "name": "审查大师",
      "avatar": "🔍",
      "description": "代码审查专家，关注代码质量、性能和安全性",
      "capabilities": ["代码审查", "最佳实践", "安全"],
      "platformId": "codex",
      "isBuiltin": true,
      "createdAt": "2026-05-20T00:00:00Z"
    }
  ]
}
```

---

### `POST /agents` — 创建自定义 Agent 角色

**用途：** 用户创建新的 Agent 角色（P1 功能）。

请求体：
```json
{
  "name": "产品经理",
  "avatar": "📋",
  "description": "擅长将需求整理成结构化的 PRD 文档",
  "capabilities": ["产品", "文档", "需求分析"],
  "systemInstruction": "你是一位资深产品经理，专注于需求文档输出...",
  "platformId": "llm"
}
```

---

### `PUT /agents/{id}` — 更新 Agent 角色

### `DELETE /agents/{id}` — 删除自定义 Agent（仅非内置）

---

## 五、Platform API

### `GET /platforms` — 获取已接入平台列表

**用途：** 设置页展示平台状态。

响应体：
```json
{
  "success": true,
  "data": [
    {
      "id": "mock",
      "name": "Mock Agent",
      "binaryPath": "",
      "config": {},
      "status": "available"
    },
    {
      "id": "llm",
      "name": "LLM Provider (火山方舟)",
      "binaryPath": "",
      "config": { "apiBase": "https://ark.cn-beijing.volces.com/api/v3", "model": "doubao-pro-32k" },
      "status": "available"
    },
    {
      "id": "opencode",
      "name": "OpenCode CLI",
      "binaryPath": "/usr/local/bin/opencode",
      "config": { "provider": "volcengine" },
      "status": "not_installed"
    },
    {
      "id": "codex",
      "name": "Codex CLI",
      "binaryPath": "/usr/local/bin/codex",
      "config": {},
      "status": "not_installed"
    }
  ]
}
```

---

### `PUT /platforms/{id}/config` — 更新平台配置

请求体：
```json
{
  "binaryPath": "/usr/local/bin/opencode",
  "config": {
    "provider": "volcengine",
    "apiKey": "sk-xxx",
    "model": "doubao-pro-32k"
  }
}
```

---

### `POST /platforms/{id}/healthcheck` — 检查平台连接

响应体：
```json
{
  "success": true,
  "data": { "status": "available", "version": "0.1.0" }
}
```

---

## 六、Artifact API

### `GET /conversations/{convId}/artifacts` — 获取会话所有产物

**用途：** 右栏预览时获取产物列表，版本历史浏览。

查询参数：`?type=code&type=webpage`

响应体：
```json
{
  "success": true,
  "data": [
    {
      "id": "art-uuid-1",
      "messageId": "msg-uuid-2",
      "type": "code",
      "title": "index.html",
      "files": [{ "name": "index.html", "content": "...", "language": "html" }],
      "diffData": null,
      "version": 2,
      "previousVersionId": "art-uuid-0",
      "previewUrl": "/preview/conv-uuid-123/index.html",
      "createdAt": "2026-05-21T11:00:00Z"
    }
  ]
}
```

---

### `GET /artifacts/{id}` — 获取单个产物详情

**用途：** 点击产物卡片时加载完整内容（含文件全文），或版本回退时获取旧版本。

响应体：
```json
{
  "success": true,
  "data": {
    "id": "art-uuid-1",
    "messageId": "msg-uuid-2",
    "type": "code",
    "title": "index.html",
    "files": [{ "name": "index.html", "content": "<!DOCTYPE html>...", "language": "html" }],
    "diffData": null,
    "version": 2,
    "previousVersionId": "art-uuid-0",
    "previewUrl": "/preview/conv-uuid-123/index.html",
    "createdAt": "2026-05-21T11:00:00Z"
  }
}
```

---

### `GET /artifacts/{id}/versions` — 获取产物版本历史

响应体：
```json
{
  "success": true,
  "data": [
    { "id": "art-uuid-0", "version": 1, "createdAt": "..." },
    { "id": "art-uuid-1", "version": 2, "createdAt": "..." }
  ]
}
```

---

## 七、Orchestrator API

### `GET /conversations/{id}/team-board` — 获取 Team Board

**用途：** 前端展示团队协作看板信息。

响应体：
```json
{
  "success": true,
  "data": {
    "conversationId": "conv-uuid-123",
    "teamMembers": [
      { "name": "代码工匠", "role": "全栈开发", "strengths": "代码生成、项目搭建" },
      { "name": "审查大师", "role": "代码审查", "strengths": "质量把控、最佳实践" }
    ],
    "teamDecisions": [
      { "decision": "使用 React 函数组件 + Hooks", "madeBy": "代码工匠", "reason": "项目简单", "createdAt": "..." }
    ],
    "codeStandards": { "naming": "组件 PascalCase", "structure": "每个组件不超过 150 行" },
    "progress": {
      "completed": ["登录页"],
      "inProgress": { "agent": "代码工匠", "task": "Todo列表组件" },
      "pending": ["删除功能"]
    },
    "agentNotes": [],
    "updatedAt": "2026-05-21T11:00:00Z"
  }
}
```

---

### `GET /conversations/{id}/project-state` — 获取项目状态

响应体：
```json
{
  "success": true,
  "data": {
    "name": "todo-app",
    "techStack": ["React", "Tailwind CSS"],
    "fileTree": ["src/App.jsx", "src/components/TodoList.jsx", "public/index.html"],
    "decisions": ["使用 localStorage 存储数据"],
    "preferences": ["按钮圆角蓝色"],
    "progress": "已完成登录页和 Todo 列表",
    "recentChanges": [
      { "file": "TodoList.jsx", "summary": "添加了 checkbox", "agent": "代码工匠" }
    ]
  }
}
```

---

## 八、Preview API

> **注意：Preview 路径不经过 `/api/v1` 前缀，直接挂载在根路径。**

### `GET /preview/{conversation_id}/*` — 静态文件预览

**用途：** iframe 加载此 URL 预览 Agent 生成的网页。此路由直接托管用户项目目录中的静态文件。

- 路径格式：`http://localhost:8000/preview/{conversation_id}/{filepath}`
- 直接返回静态文件内容（HTML/CSS/JS/图片）
- 响应 Header 包含 `Content-Type` 和 CSP 安全头
- 支持相对路径资源引用
- 不返回 `ApiResponse` 包装，直接返回文件原始内容

示例：
```
GET /preview/conv-uuid-123/index.html  → 返回 HTML 文件（text/html）
GET /preview/conv-uuid-123/styles.css  → 返回 CSS 文件（text/css）
GET /preview/conv-uuid-123/app.js      → 返回 JS 文件（application/javascript）
```

---

## 九、SkillRule API

### `GET /skill-rules` — 获取所有规则

响应体：
```json
{
  "success": true,
  "data": [
    {
      "id": "rule-uuid-1",
      "name": "代码生成后自动审查",
      "description": "当代码工匠生成代码后，自动触发审查大师进行代码审查",
      "trigger": "after_code_generation",
      "triggerCondition": "",
      "action": {
        "agentId": "agent-uuid-2",
        "instruction": "请审查以上代码，关注质量和安全性"
      },
      "enabled": true,
      "createdAt": "2026-05-21T00:00:00Z"
    }
  ]
}
```

---

### `POST /skill-rules` — 创建规则

### `PUT /skill-rules/{id}` — 更新规则

### `DELETE /skill-rules/{id}` — 删除规则

---

## 十、WebSocket 协议

### 连接

```
ws://localhost:8000/ws/{conversation_id}
```

连接后服务器推送历史未读消息（如有）。

---

### 客户端 → 服务器

#### 发送消息（首选方式）

```json
{
  "type": "send_message",
  "data": {
    "content": "@代码工匠 帮我生成一个登录页面",
    "mentions": [{ "agentId": "agent-uuid-1", "agentName": "代码工匠" }],
    "parentMessageId": null
  }
}
```

#### 停止生成

```json
{
  "type": "stop_generation",
  "data": { "messageId": "msg-uuid-xxx" }
}
```

---

### 服务器 → 客户端

> 所有下行消息为 discriminated union：`type` 字段唯一确定 `data` 结构。

#### `agent_thinking` — Agent 开始思考

```json
{
  "type": "agent_thinking",
  "data": { "agentId": "agent-uuid-1", "agentName": "代码工匠" }
}
```

#### `text_delta` — 流式文本片段

```json
{
  "type": "text_delta",
  "data": {
    "messageId": "msg-uuid-agent-1",
    "agentName": "代码工匠",
    "delta": "好的，我来为你"
  }
}
```

> 前端持续拼接 delta 直到收到 `message_done`。

#### `orchestrator_status` — Orchestrator 分派状态

```json
{
  "type": "orchestrator_status",
  "data": {
    "status": "executing",
    "tasks": [
      { "id": "task-1", "agentId": "agent-uuid-1", "agentName": "代码工匠", "instruction": "生成 Todo 页面", "status": "running", "dependsOn": null },
      { "id": "task-2", "agentId": "agent-uuid-2", "agentName": "审查大师", "instruction": "代码审查", "status": "pending", "dependsOn": "task-1" }
    ]
  }
}
```

#### `artifact` — 产物卡片推送

```json
{
  "type": "artifact",
  "data": {
    "messageId": "msg-uuid-agent-1",
    "artifact": {
      "id": "art-uuid-1",
      "type": "webpage",
      "title": "页面预览",
      "files": [{ "name": "index.html", "content": "...", "language": "html" }],
      "diffData": null,
      "version": 1,
      "previousVersionId": null,
      "previewUrl": "/preview/conv-uuid-123/index.html",
      "createdAt": "2026-05-21T11:01:00Z"
    }
  }
}
```

#### `artifact` (Diff 类型)

```json
{
  "type": "artifact",
  "data": {
    "messageId": "msg-uuid-agent-1",
    "artifact": {
      "id": "art-uuid-2",
      "type": "diff",
      "title": "index.html 变更",
      "files": [],
      "diffData": {
        "file": "index.html",
        "hunks": [{ "oldStart": 10, "oldLines": 3, "newStart": 10, "newLines": 5, "content": "@@ -10,3 +10,5 @@\n..." }],
        "additions": 5,
        "deletions": 2
      },
      "version": 2,
      "previousVersionId": "art-uuid-1",
      "previewUrl": "/preview/conv-uuid-123/index.html"
    }
  }
}
```

#### `team_activity` — Team Protocol 消息

```json
{
  "type": "team_activity",
  "data": {
    "fromAgent": "代码工匠",
    "to": "all",
    "content": "采用 props drilling 传递数据，组件拆分为 TodoList + TodoItem",
    "noteType": "decision"
  }
}
```

#### `message_done` — 消息生成完成

```json
{
  "type": "message_done",
  "data": {
    "messageId": "msg-uuid-agent-1",
    "agentName": "代码工匠"
  }
}
```

#### `error` — 错误

```json
{
  "type": "error",
  "data": {
    "messageId": "msg-uuid-agent-1",
    "error": "Agent 进程超时（60s）",
    "recoverable": true
  }
}
```

---

## 十一、完整交互时序示例

### 群聊协作（@代码工匠 + @审查大师）

```
Client                    Server                    Agent Processes
  |                         |                         |
  |-- WS: send_message ---->|                         |
  |   @代码工匠 @审查大师    |                         |
  |                         |                         |
  |<-- orchestrator_status -|  status: dispatching    |
  |    tasks: [A:pending,   |                         |
  |            B:pending]   |                         |
  |                         |                         |
  |<-- orchestrator_status -|  status: executing      |
  |    tasks: [A:running,   |---- run_task(A) ------->|
  |            B:pending]   |                         |
  |                         |                         |
  |<-- agent_thinking ------|  代码工匠               |
  |<-- text_delta ----------|<-- event stream --------|
  |<-- text_delta ----------|                         |
  |<-- text_delta ----------|                         |
  |<-- artifact (code) -----|<-- file_created --------|
  |<-- artifact (webpage) --|                         |
  |<-- team_activity -------|<-- team_note ---------- |
  |<-- message_done --------|<-- done ----------------|
  |                         |                         |
  |<-- orchestrator_status -|  A:completed, B:running |
  |                         |---- run_task(B) ------->|
  |                         |                         |
  |<-- agent_thinking ------|  审查大师               |
  |<-- text_delta ----------|<-- event stream --------|
  |<-- artifact (diff) -----|                         |
  |<-- team_activity -------|<-- team_note ---------- |
  |<-- message_done --------|<-- done ----------------|
  |                         |                         |
  |<-- orchestrator_status -|  all completed          |
  |<-- text_delta ----------|  Orch 汇总消息          |
  |<-- message_done --------|                         |
  |                         |                         |
```

---

*API 规范文档 v1.1 — 契约一致性修复：Mention 类型化、WS discriminated union、Preview 路径独立、REST fallback 定位明确。*
