# AgentHub 技术设计文档

> 版本：v1.0 | 更新日期：2026-05-21 | 基于 PRD v1.6

---

## 一、技术选型

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|---------|
| **前端框架** | React 18 + Vite | 5.x | 纯 SPA，生态成熟，组件库丰富 |
| **状态管理** | Zustand | 4.x | 轻量、无 boilerplate、支持中间件 |
| **UI 组件** | Ant Design / shadcn/ui | - | 快速搭建 IM 风格界面 |
| **代码编辑器** | Monaco Editor | - | VS Code 同款，支持语法高亮/Diff |
| **后端框架** | Python FastAPI | 0.100+ | 异步原生、WebSocket 支持、类型安全 |
| **WebSocket** | FastAPI 原生 WebSocket | - | 无额外依赖，够用 |
| **数据库** | SQLite (开发) / PostgreSQL (生产) | - | SQLAlchemy ORM 抽象，随时切换 |
| **ORM** | SQLAlchemy 2.0 + Alembic | - | 异步支持、迁移管理 |
| **进程管理** | asyncio.subprocess | - | 管理 Agent CLI 子进程 |
| **文件监控** | watchdog | - | 跨平台文件系统事件监控 |
| **Diff 计算** | difflib (Python) + diff2html (前端) | - | 标准 unified diff 格式 |

---

## 二、系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端 (Browser)                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  React SPA (Vite)                                         │  │
│  │  ├── Pages: Login / Workspace / AgentManage / Settings    │  │
│  │  ├── Store: Zustand (conversations, messages, artifacts)  │  │
│  │  ├── WS Client: 流式消息接收 + 状态推送                     │  │
│  │  └── Components: ChatFlow / PreviewPanel / Cards          │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │  HTTP REST + WebSocket (ws://)
┌────────────────────────────▼────────────────────────────────────┐
│                       后端服务 (FastAPI)                           │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────┐  │
│  │  REST API   │  │  WS Server  │  │  Orchestrator Service  │  │
│  │  /api/v1/*  │  │  /ws/{conv} │  │  (DeepSeek LLM 直调)    │  │
│  └─────────────┘  └─────────────┘  └────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Agent Manager (进程生命周期管理)                          │    │
│  │  ├── OpenCodeAdapter  (CLI 子进程, DeepSeek 后端)        │    │
│  │  ├── CodexAdapter     (CLI 子进程, OpenAI/DeepSeek)      │    │
│  │  └── ProcessPool      (进程池/会话复用)                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐      │
│  │ Artifact Svc │  │ Preview Svc  │  │ FileWatcher Svc  │      │
│  │ (产物解析)    │  │ (静态托管)    │  │ (目录监控)        │      │
│  └──────────────┘  └──────────────┘  └──────────────────┘      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Team Protocol Service                                   │    │
│  │  ├── TeamBoard (共享看板 CRUD)                           │    │
│  │  ├── AgentNotes (便签管理)                               │    │
│  │  └── ProjectState (项目状态自动维护)                      │    │
│  └─────────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────────┤
│  数据层                                                          │
│  ├── SQLite / PostgreSQL (元数据持久化)                          │
│  ├── 本地文件系统 (用户项目目录 + 产物文件)                       │
│  └── 内存缓存 (WebSocket 会话状态, 流式 buffer)                  │
├─────────────────────────────────────────────────────────────────┤
│  外部依赖                                                        │
│  ├── OpenCode CLI 进程 (Go binary)                              │
│  ├── Codex CLI 进程 (Node.js)                                   │
│  └── DeepSeek API (Orchestrator / LLMProvider 调用)              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、项目目录结构

```
AgentHub/
├── docs/                          # 文档
│   ├── PRD.md
│   ├── TECH_DESIGN.md
│   └── 课题题目描述与详细解析.md
│
├── frontend/                      # 前端 React SPA
│   ├── public/
│   ├── src/
│   │   ├── main.tsx              # 入口
│   │   ├── App.tsx               # 路由
│   │   ├── pages/                # 页面
│   │   │   ├── Login.tsx
│   │   │   ├── Workspace.tsx     # 主工作台（三栏）
│   │   │   ├── AgentManage.tsx
│   │   │   └── Settings.tsx
│   │   ├── components/           # 组件
│   │   │   ├── chat/             # 聊天相关
│   │   │   │   ├── ConversationList.tsx
│   │   │   │   ├── ChatArea.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── MessageInput.tsx
│   │   │   │   ├── MentionSelector.tsx
│   │   │   │   └── TeamActivityCard.tsx
│   │   │   ├── cards/            # 产物卡片
│   │   │   │   ├── CodeCard.tsx
│   │   │   │   ├── DiffCard.tsx
│   │   │   │   ├── WebPreviewCard.tsx
│   │   │   │   └── OrchestratorStatus.tsx
│   │   │   ├── preview/          # 右栏预览
│   │   │   │   ├── PreviewPanel.tsx
│   │   │   │   ├── IframePreview.tsx
│   │   │   │   ├── CodeEditor.tsx
│   │   │   │   └── DiffViewer.tsx
│   │   │   └── common/           # 通用
│   │   │       ├── AgentAvatar.tsx
│   │   │       ├── Skeleton.tsx
│   │   │       └── Layout.tsx
│   │   ├── stores/               # Zustand 状态
│   │   │   ├── conversationStore.ts
│   │   │   ├── messageStore.ts
│   │   │   ├── agentStore.ts
│   │   │   ├── artifactStore.ts
│   │   │   └── uiStore.ts
│   │   ├── services/             # API/WS 通信
│   │   │   ├── api.ts            # REST API 封装
│   │   │   ├── websocket.ts      # WebSocket 客户端
│   │   │   └── types.ts          # TypeScript 类型定义
│   │   ├── hooks/                # 自定义 Hooks
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useAutoScroll.ts
│   │   │   └── useStreamMessage.ts
│   │   └── utils/                # 工具函数
│   │       ├── diff.ts
│   │       └── format.ts
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                       # 后端 Python FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI 入口
│   │   ├── config.py             # 配置管理
│   │   ├── api/                  # REST API 路由
│   │   │   ├── __init__.py
│   │   │   ├── conversations.py  # 会话 CRUD
│   │   │   ├── messages.py       # 消息 CRUD + 发送
│   │   │   ├── agents.py         # Agent 角色 CRUD
│   │   │   ├── platforms.py      # 平台管理
│   │   │   └── settings.py       # 系统设置
│   │   ├── ws/                   # WebSocket
│   │   │   ├── __init__.py
│   │   │   ├── manager.py        # 连接管理器
│   │   │   └── handlers.py       # 消息处理
│   │   ├── services/             # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py   # Orchestrator 服务
│   │   │   ├── agent_manager.py  # Agent 进程管理
│   │   │   ├── artifact_service.py  # 产物生成
│   │   │   ├── preview_service.py   # 预览服务
│   │   │   ├── file_watcher.py      # 文件监控
│   │   │   ├── team_protocol.py     # Team Protocol
│   │   │   └── project_state.py     # 项目状态管理
│   │   ├── adapters/             # Agent 平台适配器
│   │   │   ├── __init__.py
│   │   │   ├── base.py           # AgentAdapter 抽象基类
│   │   │   ├── mock.py           # MockAdapter（永久组件，开发/测试/兜底）
│   │   │   ├── llm_provider.py   # LLM 直调 Provider（DeepSeek/OpenAI 兼容）
│   │   │   ├── opencode.py       # OpenCode 适配器
│   │   │   └── codex.py          # Codex 适配器
│   │   ├── models/               # 数据库模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── agent.py
│   │   │   ├── conversation.py
│   │   │   ├── message.py
│   │   │   └── artifact.py
│   │   └── schemas/              # Pydantic 请求/响应 Schema
│   │       ├── __init__.py
│   │       ├── conversation.py
│   │       ├── message.py
│   │       └── agent.py
│   ├── alembic/                  # 数据库迁移
│   ├── tests/
│   ├── requirements.txt
│   └── alembic.ini
│
├── .claude/                       # Claude Code 配置
├── .gitignore
└── README.md
```

---

## 四、Mock-first 开发原则（最高优先级）

> **核心原则：所有真实 Agent Provider 必须有 Mock Provider 兜底。第一周不应该卡在真实 CLI 上。**

### 4.1 开发顺序（严格遵守）

```
Phase 1 (Day 1-4): Mock 闭环
─────────────────────────────
MockAdapter + FakeArtifactProvider → 前端完整 UI 闭环
  · Mock 流式文本输出
  · Mock 代码文件生成 → CodeCard 展示
  · Mock Diff 产物 → DiffCard 展示
  · Mock 网页预览 → iframe 渲染
  · Mock Team Activity 消息
目标：即使永远不接真实 CLI，Demo 也能完整跑通

Phase 2 (Day 5-8): LLM Provider 中间层
─────────────────────────────────────────
LLMProviderAdapter (DeepSeek / OpenAI 兼容 API 直调)
  · 真实 LLM 生成代码文本
  · 后端解析 LLM 输出 → 写入文件 → 生成产物
  · 比 Mock 更真实，但不依赖 CLI
目标：使用私人 DeepSeek API 即可快速联调，无需等 CLI 调通

Phase 3 (Day 8-14): 真实 CLI 接入
─────────────────────────────────────
OpenCodeAdapter / CodexAdapter (真实 CLI 子进程)
  · 调研确认接入方式
  · 如果成功 → 替换 LLM Provider
  · 如果失败 → 降级到 Phase 2，Demo 照跑
目标：锦上添花，非必须
```

### 4.2 降级策略（三级保障）

```
┌────────────────────────────────────────────────────────────────┐
│  Level 1 (最优): 真实 CLI Agent                                 │
│  OpenCode CLI / Codex CLI 子进程                                │
│  · Agent 自带完整 harness (文件操作/命令执行)                    │
│  · 输出最真实                                                   │
│  · 风险：接入方式不确定，可能失败                                │
├────────────────────────────────────────────────────────────────┤
│  Level 2 (降级): LLM Provider 直调                              │
│  DeepSeek / OpenAI 兼容 API + 后端代码解析 + 文件写入             │
│  · LLM 生成代码，后端解析并写入项目目录                          │
│  · 不如真实 Agent 强，但能展示完整产品流程                       │
│  · 评委看到的效果与 Level 1 几乎相同                             │
├────────────────────────────────────────────────────────────────┤
│  Level 3 (兜底): MockAdapter                                    │
│  预制的代码模板 + 模拟延时 + 写入固定文件                        │
│  · 用于开发阶段前端联调                                         │
│  · 用于测试                                                     │
│  · 用于 Demo 兜底（如果所有 API 都挂了）                         │
│  · 永久保留，不删除                                             │
└────────────────────────────────────────────────────────────────┘
```

### 4.3 MockAdapter 不是临时工具

MockAdapter 是**永久的一等公民**，作用包括：

| 场景 | 作用 |
|------|------|
| 前端开发 | 无需后端 Agent 即可完整调试 UI |
| 集成测试 | 确定性输出，方便自动化测试 |
| CI/CD | 无 API Key 也能跑通流程 |
| Demo 兜底 | 真实 API 出问题时切换到 Mock |
| 新成员上手 | 不需要配置 CLI/API 就能看到完整流程 |

---

## 五、后端核心设计

### 5.1 Agent Adapter 抽象接口（重设计）

```python
# backend/app/adapters/base.py

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional
from dataclasses import dataclass, field

@dataclass
class AgentEvent:
    """Agent 输出的事件流"""
    type: str       # "text_delta" | "file_created" | "file_modified" | "done" | "error" | "team_note"
    content: str = ""
    metadata: dict = field(default_factory=dict)

@dataclass
class TaskContext:
    """传递给 Agent 的结构化上下文"""
    system_instruction: str = ""       # Layer 0: Agent 基础指令
    project_state: dict = field(default_factory=dict)  # Layer 1: 项目全局状态
    relevant_files: list = field(default_factory=list)  # Layer 2: 相关文件内容
    relevant_history: list = field(default_factory=list)  # Layer 2: 相关对话历史
    team_board: dict = field(default_factory=dict)  # Team Protocol 信息
    team_notes: list = field(default_factory=list)   # 来自队友的便签

@dataclass 
class AgentSession:
    """一个 Agent 会话实例（会话型 Agent 使用）"""
    id: str
    platform: str
    process_pid: Optional[int] = None
    work_dir: str = ""
    status: str = "idle"  # "idle" | "running" | "stopped"


class AgentAdapter(ABC):
    """
    Agent 平台适配器抽象基类。
    
    核心接口是 run_task()，所有 Adapter 必须实现。
    会话式接口（start_session/send_message/stop_session）是可选扩展。
    """
    
    platform_name: str  # "mock" | "llm" | "opencode" | "codex"
    
    # ═══════════════════════════════════════════════════════
    # 核心接口：任务式调用（所有 Adapter 必须实现）
    # ═══════════════════════════════════════════════════════
    
    @abstractmethod
    async def run_task(
        self,
        work_dir: str,
        instruction: str,
        context: TaskContext,
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        执行一个任务，流式返回事件。
        
        这是唯一的必须接口。各 Adapter 的实现方式：
        - MockAdapter: 直接 yield 预制事件
        - LLMProviderAdapter: 调用 LLM API，解析输出写入文件
        - OpenCodeAdapter: 内部复用/创建 session，发送消息
        - CodexAdapter: 每次启动新进程执行任务
        
        Args:
            work_dir: 用户指定的项目目录
            instruction: 当前任务指令（用户消息）
            context: 结构化上下文（四层上下文 + Team Protocol）
        
        Yields:
            AgentEvent: 流式事件（文本片段、文件变更、完成、错误等）
        """
        pass
    
    # ═══════════════════════════════════════════════════════
    # 基础接口：健康检查
    # ═══════════════════════════════════════════════════════
    
    @abstractmethod
    async def health_check(self) -> bool:
        """检查该 Adapter 是否可用"""
        pass
    
    # ═══════════════════════════════════════════════════════
    # 可选接口：会话式调用（长会话 Agent 可覆盖）
    # ═══════════════════════════════════════════════════════
    
    async def start_session(self, work_dir: str, system_instruction: str = "") -> AgentSession:
        """可选：启动一个持久会话（OpenCode 等长会话 Agent 使用）"""
        raise NotImplementedError("This adapter does not support sessions")
    
    async def send_message(self, session: AgentSession, message: str) -> AsyncGenerator[AgentEvent, None]:
        """可选：在已有会话中发送消息"""
        raise NotImplementedError("This adapter does not support sessions")
    
    async def stop_session(self, session: AgentSession) -> None:
        """可选：停止会话"""
        raise NotImplementedError("This adapter does not support sessions")
```

### 5.2 MockAdapter 实现（永久组件）

```python
# backend/app/adapters/mock.py

import asyncio
import os
from typing import AsyncGenerator
from .base import AgentAdapter, AgentEvent, TaskContext

# 预制的代码模板
MOCK_LOGIN_HTML = '''<!DOCTYPE html>
<html><head><title>Login</title>
<style>
body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f5f5f5; }
.login-card { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); width: 320px; }
h1 { text-align: center; color: #333; }
input { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
button { width: 100%; padding: 12px; background: #4A90D9; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; }
button:hover { background: #357ABD; }
</style></head>
<body><div class="login-card"><h1>Login</h1>
<input type="text" placeholder="Username">
<input type="password" placeholder="Password">
<button>Sign In</button>
</div></body></html>'''

MOCK_REVIEW_REPORT = """## Code Review Report

### Summary
Overall code quality: **Good** (7/10)

### Issues Found
1. **[Warning]** Missing input validation on form fields
2. **[Suggestion]** Consider adding aria-labels for accessibility
3. **[Suggestion]** Button could use :focus-visible style for keyboard navigation

### Positive Points
- Clean semantic HTML structure
- Good use of CSS custom properties potential
- Responsive-friendly layout approach"""


class MockAdapter(AgentAdapter):
    """
    Mock Agent 适配器 — 永久组件。
    
    用途：
    1. 前端开发联调（无需真实 Agent）
    2. 集成测试（确定性输出）
    3. Demo 兜底（真实 API 不可用时）
    """
    
    platform_name = "mock"
    
    def __init__(self, response_delay: float = 0.05, role: str = "coder"):
        """
        Args:
            response_delay: 模拟流式输出的字符间延时（秒）
            role: "coder" | "reviewer" | "doc" — 决定模拟行为
        """
        self.response_delay = response_delay
        self.role = role
    
    async def health_check(self) -> bool:
        return True  # Mock 永远可用
    
    async def run_task(
        self, work_dir: str, instruction: str, context: TaskContext
    ) -> AsyncGenerator[AgentEvent, None]:
        """模拟 Agent 执行任务"""
        
        if self.role == "coder":
            async for event in self._mock_code_generation(work_dir, instruction):
                yield event
        elif self.role == "reviewer":
            async for event in self._mock_code_review(work_dir, instruction):
                yield event
        else:
            async for event in self._mock_text_response(instruction):
                yield event
    
    async def _mock_code_generation(self, work_dir: str, instruction: str) -> AsyncGenerator[AgentEvent, None]:
        """模拟代码生成 Agent"""
        
        # 1. 流式文本输出
        response_text = "好的，我来为你生成代码。正在分析需求并创建文件...\n\n"
        for char in response_text:
            yield AgentEvent(type="text_delta", content=char)
            await asyncio.sleep(self.response_delay)
        
        # 2. 模拟写入文件
        filepath = os.path.join(work_dir, "index.html")
        os.makedirs(work_dir, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(MOCK_LOGIN_HTML)
        
        yield AgentEvent(
            type="file_created",
            content=filepath,
            metadata={"filename": "index.html", "language": "html", "lines": MOCK_LOGIN_HTML.count('\n')}
        )
        
        # 3. 完成文本
        done_text = f"\n✅ 已创建 `index.html`，包含一个简洁的登录页面。"
        for char in done_text:
            yield AgentEvent(type="text_delta", content=char)
            await asyncio.sleep(self.response_delay)
        
        # 4. Team Note
        yield AgentEvent(
            type="team_note",
            content="",
            metadata={
                "to": "all",
                "decisions": ["使用纯 HTML+CSS，无 JS 框架依赖", "采用 flexbox 居中布局"],
                "heads_up": "表单未做验证，等下次任务添加",
            }
        )
        
        # 5. 完成事件
        yield AgentEvent(type="done", content="")
    
    async def _mock_code_review(self, work_dir: str, instruction: str) -> AsyncGenerator[AgentEvent, None]:
        """模拟代码审查 Agent"""
        for char in MOCK_REVIEW_REPORT:
            yield AgentEvent(type="text_delta", content=char)
            await asyncio.sleep(self.response_delay * 0.5)
        
        yield AgentEvent(
            type="team_note",
            content="",
            metadata={
                "to": "coder",
                "decisions": ["当前代码结构合理，无需大改"],
                "heads_up": "建议下次添加 aria-label 属性",
            }
        )
        yield AgentEvent(type="done", content="")
    
    async def _mock_text_response(self, instruction: str) -> AsyncGenerator[AgentEvent, None]:
        """模拟通用文本回复"""
        response = f"收到你的请求：「{instruction}」\n\n我已经分析了需求，这是我的输出...\n"
        for char in response:
            yield AgentEvent(type="text_delta", content=char)
            await asyncio.sleep(self.response_delay)
        yield AgentEvent(type="done", content="")
```

### 5.3 LLMProviderAdapter 实现思路（中间态）

```python
# backend/app/adapters/llm_provider.py

import httpx
import json
import os
from typing import AsyncGenerator
from .base import AgentAdapter, AgentEvent, TaskContext

class LLMProviderAdapter(AgentAdapter):
    """
    LLM 直调适配器 — 作为 Mock 和真实 CLI 之间的中间层。
    
    工作方式：
    1. 调用 OpenAI 兼容格式的 LLM API（默认 DeepSeek，也可兼容 OpenAI 等）
    2. LLM 生成包含代码的回复
    3. 后端解析回复中的代码块，写入项目目录
    4. 生成对应的产物事件
    
    兼容：DeepSeek、OpenAI、Moonshot 等 OpenAI 格式 API。
    """
    
    platform_name = "llm"
    
    def __init__(self, api_base: str, api_key: str, model: str):
        self.api_base = api_base.rstrip('/')
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def health_check(self) -> bool:
        try:
            resp = await self.client.get(f"{self.api_base}/models",
                headers={"Authorization": f"Bearer {self.api_key}"})
            return resp.status_code == 200
        except Exception:
            return False
    
    async def run_task(
        self, work_dir: str, instruction: str, context: TaskContext
    ) -> AsyncGenerator[AgentEvent, None]:
        """调用 LLM API 生成代码，解析输出并写入文件"""
        
        # 构建 prompt
        messages = self._build_messages(instruction, context)
        
        # 流式调用 LLM
        accumulated_text = ""
        async for chunk in self._stream_chat(messages):
            yield AgentEvent(type="text_delta", content=chunk)
            accumulated_text += chunk
        
        # 解析完成后的文本，提取代码块并写入文件
        code_blocks = self._extract_code_blocks(accumulated_text)
        for block in code_blocks:
            filepath = os.path.join(work_dir, block["filename"])
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(block["content"])
            
            yield AgentEvent(
                type="file_created",
                content=filepath,
                metadata={"filename": block["filename"], "language": block["language"]}
            )
        
        yield AgentEvent(type="done", content="")
    
    async def _stream_chat(self, messages: list) -> AsyncGenerator[str, None]:
        """流式调用 OpenAI 兼容 API"""
        async with self.client.stream(
            "POST",
            f"{self.api_base}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "messages": messages, "stream": True},
        ) as response:
            async for line in response.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    data = json.loads(line[6:])
                    delta = data["choices"][0].get("delta", {}).get("content", "")
                    if delta:
                        yield delta
    
    def _extract_code_blocks(self, text: str) -> list:
        """从 LLM 输出中提取 ```code``` 块"""
        import re
        pattern = r'```(\w+)?\s*\n(?:#\s*filename:\s*(.+?)\n)?(.*?)```'
        blocks = []
        for match in re.finditer(pattern, text, re.DOTALL):
            language = match.group(1) or "text"
            filename = match.group(2) or f"output.{language}"
            content = match.group(3).strip()
            blocks.append({"language": language, "filename": filename.strip(), "content": content})
        return blocks
    
    def _build_messages(self, instruction: str, context: TaskContext) -> list:
        """构建 LLM 消息"""
        system = context.system_instruction or "你是一个全栈开发专家。"
        system += "\n\n请在代码块中标注文件名，格式：```language\n# filename: path/to/file\n代码内容\n```"
        
        user_content = ""
        if context.project_state:
            user_content += f"【项目状态】\n{json.dumps(context.project_state, ensure_ascii=False)}\n\n"
        if context.relevant_files:
            user_content += "【相关文件】\n" + "\n".join(
                f"--- {f['name']} ---\n{f['content']}" for f in context.relevant_files
            ) + "\n\n"
        user_content += f"【任务】\n{instruction}"
        
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ]
```

### 5.4 OpenCode Adapter 实现思路

```python
# backend/app/adapters/opencode.py

import asyncio
import json
from typing import AsyncGenerator
from .base import AgentAdapter, AgentEvent, AgentSession, TaskContext

class OpenCodeAdapter(AgentAdapter):
    """
    OpenCode CLI 适配器。
    内部维护 session（长会话），但对外暴露 run_task() 统一接口。
    """
    platform_name = "opencode"
    
    def __init__(self, binary_path: str = "opencode", model_config: dict = None):
        self.binary_path = binary_path
        self.model_config = model_config or {}
        self._sessions: dict[str, tuple[AgentSession, asyncio.subprocess.Process]] = {}
    
    async def health_check(self) -> bool:
        """检查 OpenCode CLI 是否已安装"""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.binary_path, "--version",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.wait()
            return proc.returncode == 0
        except FileNotFoundError:
            return False
    
    async def run_task(
        self, work_dir: str, instruction: str, context: TaskContext
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        执行任务。内部逻辑：
        - 如果该 work_dir 已有活跃 session → 复用（send_message）
        - 如果没有 → 新建 session
        """
        session_key = f"opencode-{work_dir}"
        
        if session_key not in self._sessions:
            session = await self.start_session(work_dir, context.system_instruction)
            self._sessions[session_key] = session
        
        session = self._sessions[session_key]
        
        # 构建完整消息（注入上下文）
        full_message = self._build_message_with_context(instruction, context)
        
        async for event in self.send_message(session, full_message):
            yield event
    
    async def start_session(self, work_dir: str, system_instruction: str = "") -> AgentSession:
        """启动 OpenCode CLI 子进程"""
        # TODO: 调研确认 OpenCode 的编程接入方式后实现
        # 备选：stdin/stdout pipe | HTTP API | gRPC
        cmd = [self.binary_path, "--work-dir", work_dir, "--non-interactive"]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=work_dir,
        )
        
        return AgentSession(
            id=f"opencode-{process.pid}",
            platform="opencode",
            process_pid=process.pid,
            work_dir=work_dir,
            status="idle",
        )
    
    async def send_message(self, session: AgentSession, message: str) -> AsyncGenerator[AgentEvent, None]:
        """在已有 session 中发送消息"""
        # TODO: 根据 OpenCode 实际输出格式实现
        yield AgentEvent(type="text_delta", content="[OpenCode] Processing...")
        yield AgentEvent(type="done", content="")
    
    async def stop_session(self, session: AgentSession) -> None:
        """停止 session"""
        pass  # TODO: kill process
    
    def _build_message_with_context(self, instruction: str, context: TaskContext) -> str:
        """将 TaskContext 拼接为发送给 Agent 的完整消息"""
        parts = []
        if context.team_board:
            parts.append(f"【团队信息】\n{json.dumps(context.team_board, ensure_ascii=False)}")
        if context.team_notes:
            parts.append("【来自队友的备忘】\n" + "\n".join(str(n) for n in context.team_notes))
        parts.append(f"【任务】\n{instruction}")
        return "\n\n".join(parts)
```

### 5.5 Codex Adapter 实现思路

```python
# backend/app/adapters/codex.py

import asyncio
import os
from typing import AsyncGenerator
from .base import AgentAdapter, AgentEvent, TaskContext

class CodexAdapter(AgentAdapter):
    """
    Codex CLI 适配器。
    每次 run_task() 启动一个新进程（一次任务一进程模式）。
    """
    platform_name = "codex"
    
    def __init__(self, binary_path: str = "codex", api_key: str = ""):
        self.binary_path = binary_path
        self.api_key = api_key
    
    async def health_check(self) -> bool:
        try:
            proc = await asyncio.create_subprocess_exec(
                self.binary_path, "--version",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            await proc.wait()
            return proc.returncode == 0
        except FileNotFoundError:
            return False
    
    async def run_task(
        self, work_dir: str, instruction: str, context: TaskContext
    ) -> AsyncGenerator[AgentEvent, None]:
        """每次任务启动新的 Codex 进程"""
        
        full_instruction = self._build_instruction(instruction, context)
        
        cmd = [
            self.binary_path,
            "--full-auto",
            "--quiet",
            "--approval-mode", "full-auto",
            full_instruction,
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=work_dir,
            env={**os.environ, "OPENAI_API_KEY": self.api_key},
        )
        
        # 流式读取 stdout
        async for line in process.stdout:
            text = line.decode().strip()
            if text:
                yield AgentEvent(type="text_delta", content=text + "\n")
        
        await process.wait()
        
        if process.returncode == 0:
            yield AgentEvent(type="done", content="", metadata={"exit_code": 0})
        else:
            stderr = await process.stderr.read()
            yield AgentEvent(type="error", content=stderr.decode(), metadata={"exit_code": process.returncode})
    
    def _build_instruction(self, instruction: str, context: TaskContext) -> str:
        """构建传给 Codex CLI 的指令字符串"""
        parts = [instruction]
        if context.team_notes:
            parts.append("Note from teammates: " + "; ".join(str(n) for n in context.team_notes))
        return " ".join(parts)
```

### 4.4 Orchestrator 服务

```python
# backend/app/services/orchestrator.py

from typing import List
from app.services.project_state import ProjectStateService
from app.adapters.base import AgentAdapter

class OrchestratorService:
    """
    Orchestrator 核心逻辑：
    1. Python 信息收集
    2. DeepSeek LLM 决策
    3. Python 执行分派
    """
    
    def __init__(self, deepseek_api_key: str, agent_manager: "AgentManager"):
        self.llm_client = OpenAICompatibleClient(
            api_key=deepseek_api_key,
            base_url="https://api.deepseek.com",
        )
        self.agent_manager = agent_manager
        self.project_state_svc = ProjectStateService()
    
    async def handle_message(self, conversation_id: str, user_message: str, mentions: List[str]):
        """处理用户消息，决策并分派"""
        
        # Step 1: 信息收集（Python 代码，快速确定性）
        conversation = await self._get_conversation(conversation_id)
        project_info = await self._collect_project_info(conversation.work_dir)
        chat_history = await self._get_relevant_history(conversation_id)
        team_board = await self._get_team_board(conversation_id)
        
        # Step 2: LLM 决策（DeepSeek API）
        dispatch_plan = await self._llm_decide(
            project_info=project_info,
            chat_history=chat_history,
            user_message=user_message,
            mentions=mentions,
            available_agents=self.agent_manager.list_agents(),
            team_board=team_board,
        )
        
        # Step 3: 执行分派（Python 代码）
        results = await self._execute_plan(dispatch_plan, conversation)
        
        # Step 4: 更新项目状态和 Team Board
        await self.project_state_svc.update_after_task(conversation.work_dir, results)
        
        return results
    
    async def _collect_project_info(self, work_dir: str) -> dict:
        """收集项目状态信息"""
        import os, subprocess
        
        # 文件结构
        file_tree = []
        for root, dirs, files in os.walk(work_dir):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '__pycache__']]
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), work_dir)
                file_tree.append(rel_path)
        
        # Git 最近变更
        try:
            git_log = subprocess.check_output(
                ["git", "log", "--oneline", "-5"],
                cwd=work_dir, text=True
            )
        except Exception:
            git_log = ""
        
        # 项目状态文档
        project_state = await self.project_state_svc.get_state(work_dir)
        
        return {
            "file_tree": file_tree[:50],  # 限制数量
            "git_log": git_log,
            "project_state": project_state,
        }
    
    async def _llm_decide(self, **kwargs) -> dict:
        """调用 DeepSeek LLM 进行任务决策"""
        prompt = self._build_orchestrator_prompt(**kwargs)
        
        response = await self.llm_client.chat(
            model="deepseek-v4-flash",
            messages=[
                {"role": "system", "content": ORCHESTRATOR_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},  # 强制 JSON 输出
        )
        
        return json.loads(response.content)
    
    async def _execute_plan(self, plan: dict, conversation) -> list:
        """执行分派计划"""
        results = []
        
        for task in plan["tasks"]:
            agent_role = task["agent"]
            instruction = task["instruction"]
            
            # 构建四层上下文
            context = await self._build_layered_context(task, conversation)
            full_message = f"{context}\n\n{instruction}"
            
            # 获取对应 Agent 的 adapter 和 session
            adapter, session = await self.agent_manager.get_or_create_session(
                agent_role, conversation.work_dir
            )
            
            # 流式执行并推送结果
            async for event in adapter.send_message(session, full_message):
                await self._push_event_to_ws(conversation.id, agent_role, event)
            
            results.append({"agent": agent_role, "status": "completed"})
            
            # 等待依赖任务（如果有）
            # ...
        
        return results
```

### 4.5 REST API 设计

```
基础路径：/api/v1

会话管理：
  POST   /conversations              创建会话
  GET    /conversations              获取会话列表
  GET    /conversations/{id}         获取会话详情
  DELETE /conversations/{id}         删除会话

消息：
  POST   /conversations/{id}/messages     发送消息（触发 Agent 调用）
  GET    /conversations/{id}/messages     获取消息历史
  POST   /messages/{id}/regenerate        重新生成某条消息

Agent 角色：
  GET    /agents                     获取所有 Agent 角色
  POST   /agents                     创建自定义 Agent 角色
  PUT    /agents/{id}                更新 Agent 角色
  DELETE /agents/{id}                删除自定义 Agent 角色

平台管理：
  GET    /platforms                   获取已接入平台列表和状态
  PUT    /platforms/{id}/config       更新平台配置
  POST   /platforms/{id}/healthcheck  检查平台连接状态

预览：
  GET    /preview/{session_id}/*      静态文件预览服务（iframe 加载）

设置：
  GET    /settings                    获取系统设置
  PUT    /settings                    更新系统设置
```

### 4.6 WebSocket 协议设计

```
连接地址：ws://localhost:8000/ws/{conversation_id}

客户端 → 服务器（上行消息）：
{
  "type": "send_message",
  "data": {
    "content": "帮我生成一个登录页",
    "mentions": ["代码工匠"]     // @ 提及的 Agent 角色名
  }
}

{
  "type": "stop_generation",     // 停止生成
  "data": { "message_id": "xxx" }
}

服务器 → 客户端（下行推送）：
// Agent 正在思考
{
  "type": "agent_thinking",
  "data": { "agent_name": "代码工匠" }
}

// Agent 流式文本输出
{
  "type": "text_delta",
  "data": {
    "message_id": "msg-xxx",
    "agent_name": "代码工匠",
    "delta": "好的，我来为你" 
  }
}

// Orchestrator 状态更新
{
  "type": "orchestrator_status",
  "data": {
    "status": "dispatching",
    "tasks": [
      {"agent": "代码工匠", "task": "生成 Todo 页面", "status": "running"},
      {"agent": "审查大师", "task": "代码审查", "status": "pending"}
    ]
  }
}

// 产物卡片推送
{
  "type": "artifact",
  "data": {
    "message_id": "msg-xxx",
    "artifact": {
      "id": "art-xxx",
      "type": "code",            // "code" | "diff" | "webpage"
      "title": "TodoList.jsx",
      "files": [{"name": "TodoList.jsx", "content": "...", "language": "jsx"}],
      "preview_url": null
    }
  }
}

// Diff 产物
{
  "type": "artifact",
  "data": {
    "message_id": "msg-xxx",
    "artifact": {
      "id": "art-yyy",
      "type": "diff",
      "title": "TodoList.jsx 变更",
      "diff_data": {
        "file": "TodoList.jsx",
        "hunks": [...],           // unified diff hunks
        "additions": 15,
        "deletions": 3
      }
    }
  }
}

// 网页预览就绪
{
  "type": "artifact",
  "data": {
    "message_id": "msg-xxx",
    "artifact": {
      "id": "art-zzz",
      "type": "webpage",
      "title": "页面预览",
      "preview_url": "/preview/session-xxx/index.html"
    }
  }
}

// Team Activity 推送
{
  "type": "team_activity",
  "data": {
    "from_agent": "代码工匠",
    "to": "all",
    "content": "采用 props drilling 传递数据，组件拆分为 TodoList + TodoItem。",
    "note_type": "decision"      // "decision" | "heads_up" | "question"
  }
}

// 消息完成
{
  "type": "message_done",
  "data": {
    "message_id": "msg-xxx",
    "agent_name": "代码工匠"
  }
}

// 错误
{
  "type": "error",
  "data": {
    "message_id": "msg-xxx",
    "error": "Agent 进程超时",
    "recoverable": true
  }
}
```

---

## 六、前端核心设计

### 5.1 路由设计

```typescript
// src/App.tsx
const routes = [
  { path: '/login', component: Login },
  { path: '/', component: Workspace },         // 主工作台
  { path: '/agents', component: AgentManage },  // Agent 管理
  { path: '/settings', component: Settings },   // 设置
];
```

### 5.2 Zustand Store 设计

```typescript
// src/stores/conversationStore.ts
interface ConversationStore {
  conversations: Conversation[];
  activeConversationId: string | null;
  loading: boolean;
  
  fetchConversations: () => Promise<void>;
  createConversation: (data: CreateConvDTO) => Promise<Conversation>;
  setActive: (id: string) => void;
  deleteConversation: (id: string) => Promise<void>;
}

// src/stores/messageStore.ts
interface MessageStore {
  messagesByConv: Record<string, Message[]>;
  streamingMessages: Record<string, string>;  // msgId → 流式累积文本
  loading: boolean;
  
  fetchMessages: (convId: string) => Promise<void>;
  appendStreamDelta: (msgId: string, delta: string) => void;
  finalizeMessage: (msgId: string, fullMessage: Message) => void;
  sendMessage: (convId: string, content: string, mentions: string[]) => void;
}

// src/stores/artifactStore.ts
interface ArtifactStore {
  artifactsByMessage: Record<string, Artifact[]>;
  activeArtifact: Artifact | null;           // 右栏当前展示
  previewPanelVisible: boolean;
  activeTab: 'preview' | 'code' | 'diff';
  
  addArtifact: (msgId: string, artifact: Artifact) => void;
  setActiveArtifact: (artifact: Artifact) => void;
  togglePreviewPanel: () => void;
  setActiveTab: (tab: string) => void;
}

// src/stores/agentStore.ts
interface AgentStore {
  agents: Agent[];
  loading: boolean;
  
  fetchAgents: () => Promise<void>;
  createAgent: (data: CreateAgentDTO) => Promise<Agent>;
  updateAgent: (id: string, data: UpdateAgentDTO) => Promise<Agent>;
}
```

### 5.3 WebSocket Hook

```typescript
// src/hooks/useWebSocket.ts
export function useWebSocket(conversationId: string | null) {
  const messageStore = useMessageStore();
  const artifactStore = useArtifactStore();
  
  useEffect(() => {
    if (!conversationId) return;
    
    const ws = new WebSocket(`ws://localhost:8000/ws/${conversationId}`);
    
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      
      switch (msg.type) {
        case 'text_delta':
          messageStore.appendStreamDelta(msg.data.message_id, msg.data.delta);
          break;
        case 'artifact':
          artifactStore.addArtifact(msg.data.message_id, msg.data.artifact);
          break;
        case 'team_activity':
          messageStore.addTeamActivity(msg.data);
          break;
        case 'orchestrator_status':
          messageStore.updateOrchestratorStatus(msg.data);
          break;
        case 'message_done':
          messageStore.finalizeMessage(msg.data.message_id);
          break;
        case 'error':
          messageStore.setError(msg.data);
          break;
      }
    };
    
    return () => ws.close();
  }, [conversationId]);
}
```

### 5.4 核心组件关系

```
Workspace (页面)
├── ConversationList (左栏)
│   ├── SearchBox
│   ├── ConversationItem × N
│   └── NewConversationButton → Modal
│
├── ChatArea (中栏)
│   ├── ChatHeader (当前Agent信息)
│   ├── MessageFlow
│   │   ├── MessageBubble (用户消息)
│   │   ├── MessageBubble (Agent消息)
│   │   │   ├── TextContent (流式渲染)
│   │   │   ├── CodeCard (内嵌代码卡片)
│   │   │   ├── DiffCard (内嵌Diff卡片)
│   │   │   └── WebPreviewCard (内嵌预览缩略图)
│   │   ├── TeamActivityCard (🤝 团队协作卡片)
│   │   └── OrchestratorStatus (任务分派状态条)
│   └── MessageInput
│       ├── TextArea (支持 @ 触发)
│       ├── MentionSelector (浮层)
│       └── SendButton
│
└── PreviewPanel (右栏，可收起)
    ├── TabBar [预览 | 代码 | Diff]
    ├── IframePreview (预览Tab)
    ├── CodeEditor (代码Tab，Monaco)
    └── DiffViewer (Diff Tab，Monaco Diff)
```

---

## 七、数据库 Schema (SQLAlchemy)

```python
# backend/app/models/

from sqlalchemy import Column, String, Text, JSON, Boolean, DateTime, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    avatar = Column(String(255), default="")
    created_at = Column(DateTime, default=datetime.utcnow)

class AgentPlatform(Base):
    __tablename__ = "agent_platforms"
    id = Column(String(50), primary_key=True)  # "opencode" | "codex"
    name = Column(String(100), nullable=False)
    binary_path = Column(String(500))
    config = Column(JSON, default={})  # api_key, model, extra_args
    status = Column(String(20), default="unknown")  # available | not_installed | error

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)       # 用户看到的角色名
    avatar = Column(String(50), default="🤖")
    description = Column(Text, default="")           # 能力描述
    capabilities = Column(JSON, default=[])          # 能力标签列表
    system_instruction = Column(Text, default="")    # 附加指令
    platform_id = Column(String(50), ForeignKey("agent_platforms.id"))
    is_builtin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    platform = relationship("AgentPlatform")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), default="新对话")
    type = Column(String(20), default="single")      # single | group
    work_dir = Column(String(500), nullable=False)   # 用户指定的项目目录
    participant_ids = Column(JSON, default=[])        # Agent ID 列表
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)         # user | agent | orchestrator | system | team_activity
    agent_id = Column(String, ForeignKey("agents.id"), nullable=True)
    content = Column(Text, default="")
    content_type = Column(String(20), default="text") # text | code | mixed
    metadata = Column(JSON, default={})               # token用量、执行时间等
    parent_message_id = Column(String, nullable=True) # 引用回复
    created_at = Column(DateTime, default=datetime.utcnow)
    
    agent = relationship("Agent")
    artifacts = relationship("Artifact", back_populates="message")

class Artifact(Base):
    __tablename__ = "artifacts"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String, ForeignKey("messages.id"), nullable=False)
    type = Column(String(20), nullable=False)         # code | webpage | diff | document
    title = Column(String(200), default="")
    files = Column(JSON, default=[])                  # [{name, content, language}]
    diff_data = Column(JSON, nullable=True)           # {hunks, additions, deletions}
    version = Column(Integer, default=1)
    previous_version_id = Column(String, nullable=True)
    preview_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    message = relationship("Message", back_populates="artifacts")

class TeamBoard(Base):
    __tablename__ = "team_boards"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), unique=True)
    team_decisions = Column(JSON, default=[])
    code_standards = Column(JSON, default={})
    progress = Column(JSON, default={})
    agent_notes = Column(JSON, default=[])
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ProjectState(Base):
    __tablename__ = "project_states"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), unique=True)
    work_dir = Column(String(500))
    state_data = Column(JSON, default={})  # 完整的 project_state 结构
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## 八、File Watcher 与产物生成

```python
# backend/app/services/file_watcher.py

import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import difflib

class ProjectFileWatcher:
    """监控用户项目目录的文件变更，生成 Diff 和产物"""
    
    def __init__(self, work_dir: str, on_change_callback):
        self.work_dir = work_dir
        self.callback = on_change_callback
        self.file_snapshots = {}  # 文件名 → 上一次内容
        self._observer = None
    
    def start(self):
        """开始监控"""
        handler = _ChangeHandler(self)
        self._observer = Observer()
        self._observer.schedule(handler, self.work_dir, recursive=True)
        self._observer.start()
    
    def stop(self):
        if self._observer:
            self._observer.stop()
    
    def snapshot_file(self, filepath: str):
        """在 Agent 操作前快照文件内容"""
        try:
            with open(filepath, 'r') as f:
                self.file_snapshots[filepath] = f.read()
        except FileNotFoundError:
            self.file_snapshots[filepath] = None  # 新文件
    
    def compute_diff(self, filepath: str) -> dict | None:
        """计算文件变更的 diff"""
        old_content = self.file_snapshots.get(filepath)
        try:
            with open(filepath, 'r') as f:
                new_content = f.read()
        except FileNotFoundError:
            return None
        
        if old_content is None:
            # 新文件
            return {
                "type": "new_file",
                "file": filepath,
                "content": new_content,
                "additions": new_content.count('\n') + 1,
                "deletions": 0,
            }
        
        if old_content == new_content:
            return None
        
        # 生成 unified diff
        diff = difflib.unified_diff(
            old_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{filepath}",
            tofile=f"b/{filepath}",
        )
        diff_text = ''.join(diff)
        
        additions = sum(1 for line in diff_text.split('\n') if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in diff_text.split('\n') if line.startswith('-') and not line.startswith('---'))
        
        return {
            "type": "modified",
            "file": filepath,
            "diff_text": diff_text,
            "additions": additions,
            "deletions": deletions,
            "old_content": old_content,
            "new_content": new_content,
        }
```

---

## 九、Preview 服务

```python
# backend/app/services/preview_service.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

class PreviewService:
    """为每个会话提供静态文件预览"""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self._mounted_sessions = set()
    
    def mount_session_preview(self, session_id: str, work_dir: str):
        """为会话挂载预览路由"""
        if session_id in self._mounted_sessions:
            return
        
        route_path = f"/preview/{session_id}"
        self.app.mount(
            route_path,
            StaticFiles(directory=work_dir, html=True),
            name=f"preview-{session_id}",
        )
        self._mounted_sessions.add(session_id)
    
    def get_preview_url(self, session_id: str, filename: str = "index.html") -> str:
        """获取预览 URL"""
        return f"/preview/{session_id}/{filename}"
    
    def unmount_session_preview(self, session_id: str):
        """移除会话预览路由"""
        # FastAPI 不直接支持动态卸载，可通过路由中间件实现
        self._mounted_sessions.discard(session_id)
```

---

## 十、关键依赖清单

### 后端 (requirements.txt)

```
# Web 框架
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
websockets>=11.0

# 数据库
sqlalchemy>=2.0
alembic>=1.12
aiosqlite             # SQLite 异步驱动（开发环境）
asyncpg               # PostgreSQL 异步驱动（生产环境，可选）

# HTTP 客户端（调 DeepSeek/OpenAI 兼容 API）
httpx>=0.25.0

# 文件监控
watchdog>=3.0

# 工具
pydantic>=2.0
python-dotenv
```

### 前端 (package.json 核心依赖)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "zustand": "^4.4.0",
    "@monaco-editor/react": "^4.6.0",
    "diff2html": "^3.4.0",
    "antd": "^5.12.0",
    "@ant-design/icons": "^5.2.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "@types/react": "^18.2.0"
  }
}
```

---

## 十一、开发环境配置

### 10.1 环境要求

| 工具 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 后端运行 |
| Node.js | 18+ | 前端开发 |
| OpenCode | latest | Agent 平台 1 |
| Codex CLI | latest | Agent 平台 2 |
| Git | 2.x | 版本管理 |

### 10.2 启动命令

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev  # http://localhost:5173

# 代理配置（vite.config.ts 中代理 /api 和 /ws 到后端）
```

### 10.3 环境变量 (.env)

```bash
# 后端配置
DATABASE_URL=sqlite+aiosqlite:///./agenthub.db
DEEPSEEK_API_KEY=your_deepseek_api_key
OPENAI_API_KEY=your_openai_api_key
OPENCODE_BINARY_PATH=/usr/local/bin/opencode
CODEX_BINARY_PATH=/usr/local/bin/codex

# DeepSeek 配置（Orchestrator / LLMProvider 用）
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 10.4 DeepSeek 成本与调用约束

DeepSeek 是比赛期间默认 LLM 后端，不计入“至少两个 Agent 平台”的平台数量；平台接入仍由 OpenCode + Codex 满足。按 2026-05-28 查询 DeepSeek 官方价格页（https://api-docs.deepseek.com/quick_start/pricing），`deepseek-v4-flash` 价格为：cache miss 输入 `$0.14 / 1M tokens`，cache hit 输入 `$0.0028 / 1M tokens`，输出 `$0.28 / 1M tokens`。价格可能变化，答辩前需复核。

工程约束：
- 后端只从环境变量读取 `DEEPSEEK_API_KEY`，不得写入仓库或返回给前端。
- LLMProvider 与 Orchestrator 默认设置单次超时、最大输出 token 和有限重试。
- 每次真实 LLM 调用记录 input/output token、模型名和估算费用到 metadata 或开发日志。
- 自动化测试默认使用 MockAdapter；端到端测试只在明确开启真实 LLM 时调用 DeepSeek。
- 如果 DeepSeek API 失败，按 `CLI → LLMProvider → MockAdapter` 策略继续保证 Demo 闭环。

---

## 十二、开发阶段规划

### M1：Mock-first 完整闭环 (Day 1-4，组长独立)

| 任务 | 产出 |
|------|------|
| 初始化前后端项目 | Vite+React 脚手架 + FastAPI 脚手架 |
| 数据库 Schema | SQLAlchemy 模型 + Alembic 初始迁移 |
| **MockAdapter 实现** | **完整的 Mock 适配器，能模拟流式文本+代码生成+Diff+TeamNote** |
| WebSocket 基础通道 | 前后端 WS 连通，Mock 事件能推送到前端 |
| 三栏 UI 框架 | Layout 骨架 + 会话列表 + 聊天区 + 预览区占位 |
| **Mock 闭环验证** | **用 MockAdapter 跑通：发消息→流式回复→代码卡片→预览，全链路** |
| API 基础框架 | 会话和消息的 CRUD 接口 |

> **M1 完成标志：不依赖任何外部 API/CLI，仅用 Mock 就能演示完整的产品核心流程。**

### M2：聊天核心 (Day 4-8，组长+小马)

| 任务 | 负责人 |
|------|--------|
| 会话列表完整交互 | 组长 |
| 消息流渲染（含流式） | 组长 |
| @ 提及 Agent 交互 | 组长 |
| **LLMProviderAdapter 实现** | **小马** |
| **DeepSeek API 接入联调** | **小马** |
| AgentAdapter 抽象基类确认 | 小马 |

### M3：真实 Agent 接入 + Orchestrator (Day 8-12，小马主导)

| 任务 | 负责人 |
|------|--------|
| **OpenCode CLI 调研+接入（尝试）** | **小马** |
| **Codex CLI 调研+接入（尝试）** | **小马** |
| 进程生命周期管理 | 小马 |
| Orchestrator 基础（@ 解析+分派） | 组长 |
| Team Board 数据结构 | 组长 |
| **如果 CLI 接入失败 → 降级到 LLMProvider** | **小马** |

### M4：产物与预览 (Day 8-14，洋芋主导)

| 任务 | 负责人 |
|------|--------|
| File Watcher 实现 | 洋芋 |
| Diff 计算 + DiffCard 组件 | 洋芋 |
| CodeCard 组件 (语法高亮) | 洋芋 |
| Monaco Editor 集成 | 洋芋 |
| iframe 预览 + Preview 服务 | 洋芋 |
| 右栏 PreviewPanel (Tab 切换) | 洋芋 |
| WebPreviewCard 组件 | 洋芋 |

### M5：体验打磨 (Day 14-17，全员)

| 任务 | 负责人 |
|------|--------|
| Team Activity 卡片 UI | 组长 |
| Agent Notes 实现 | 组长 |
| 自定义 Agent 角色 CRUD | 小马 |
| 版本历史 | 洋芋 |
| 错误处理 + 重试 | 全员 |
| 交互动画 + 加载态 | 全员 |

### M6：交付 (Day 17-20，全员)

| 任务 | 负责人 |
|------|--------|
| 端到端测试 + Bug 修复 | 全员 |
| Demo 场景准备 | 组长 |
| 产品设计文档定稿 | 组长 |
| 技术设计文档定稿 | 全员 |
| 3 分钟 Demo 视频录制 | 组长 |
| AI 协作开发记录整理 | 全员 |

---

## 十三、关键技术风险与应对

| 风险 | 应对方案 |
|------|---------|
| **OpenCode CLI 无法编程接入** | **三级降级：CLI → LLMProvider 直调 → MockAdapter。Demo 不受影响。** |
| **Codex full-auto 模式不稳定** | **同上降级策略。另：设置超时（60s），失败走 LLMProvider。** |
| **CLI 输出格式无法解析** | **LLMProviderAdapter 作为永久 Plan B，可直接展示代码生成能力** |
| DeepSeek API 调用失败或额度异常 | Orchestrator 先用规则引擎决策；Agent 层先用 MockAdapter；API 恢复后切 LLMProvider |
| WebSocket 断连 | 前端自动重连（指数退避），重连后同步缺失消息 |
| Agent 进程内存泄漏 | 设置进程存活时间上限（30min），超时自动回收 |
| Diff 计算对大文件慢 | 限制 Diff 展示的文件大小（< 100KB），超出只展示摘要 |
| iframe 预览安全风险 | sandbox 属性 + CSP header，禁止访问父页面 |

### 降级策略详解

```
评委看到的效果：
┌────────────────────────────────────────────────────────┐
│  无论用 Level 1/2/3，评委看到的产品体验是一样的：        │
│  · 聊天消息流式输出 ✓                                  │
│  · 代码卡片展示 ✓                                      │
│  · Diff 视图 ✓                                         │
│  · iframe 网页预览 ✓                                   │
│  · 多 Agent 协作 + Team Activity ✓                     │
│                                                        │
│  区别只在于生成质量：                                    │
│  Level 1 (CLI): 真实 Agent，质量最高                    │
│  Level 2 (LLM): LLM 直调，质量够用                     │
│  Level 3 (Mock): 预制内容，仅兜底                       │
└────────────────────────────────────────────────────────┘
```

---

## 十四、待调研事项（非阻塞）

> 以下事项需要调研，但**不阻塞开发进度**——Mock-first 策略保证即使这些全部未确认，项目也能正常推进。

1. **OpenCode 编程接入方式**：是否支持 stdin/stdout pipe？是否有 HTTP API？输出格式？→ 失败则降级 LLMProvider
2. **Codex CLI full-auto 输出**：stdout 格式是纯文本还是结构化？如何识别任务完成？→ 失败则降级 LLMProvider
3. **DeepSeek API 细节**：确认 `deepseek-v4-flash` 模型 ID、流式输出、JSON 模式、工具调用支持和价格 → 至少支持 OpenAI 兼容格式
4. **跨平台兼容**：Windows (开发环境) 上 OpenCode/Codex 的运行情况 → 不兼容则 Demo 时用 Linux
5. **Monaco Editor bundle 大小**：是否需要 Code Splitting 或 Web Worker 加载 → 不影响核心流程

---

*技术设计文档 v1.1 - 重大更新：新增 Mock-first 原则、三级降级策略、重设计 AgentAdapter 接口(run_task)。*
