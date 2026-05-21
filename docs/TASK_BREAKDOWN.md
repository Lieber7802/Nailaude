# AgentHub 任务拆解与分工

> 版本：v1.0 | 基于 PRD v1.6 + TECH_DESIGN v1.1  
> 总工期：20 天 | 团队：3 人

---

## 一、团队情况与分工原则

### 人员画像

| 成员 | 投入度 | 可用时间 | 擅长领域 | 核心职责 |
|------|--------|---------|---------|---------|
| **组长（你）** | ~50% 工作量 | Day 1 起全程 | 架构设计、前端交互、Orchestrator | 搭建基础框架、前端核心、调度逻辑、项目管理 |
| **小马** | ~25% 工作量 | Day 5 起逐步投入，Day 7 全力 | LLM/算法方向 | Agent Adapter 层、LLM Provider、火山方舟接入 |
| **洋芋** | ~25% 工作量 | Day 8 起全力投入 | 全栈、什么都能做 | 产物卡片、预览系统、Diff 视图、代码编辑器 |

### 分工原则

1. **组长先行**：Day 1-7 组长独立搭建完整框架（Mock 闭环），让后来者有现成代码可接
2. **接口先行**：组长定义好所有 Adapter 接口和数据结构，小马/洋芋只需"填空"实现
3. **Mock-first**：任何模块开发前先有 Mock，不被外部依赖阻塞
4. **可并行**：M2/M3/M4 三条线尽量互不阻塞

---

## 二、里程碑概览

```
Day:  1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20
      ├───────────────────┤
      │  M1: Mock闭环(组长) │
      │                   ├───────────────────┤
      │                   │  M2: 聊天核心      │
      │                   │  (组长+小马)       │
      │                        ├─────────────────────────┤
      │                        │  M3: Agent接入(小马)     │
      │                             ├────────────────────────────┤
      │                             │  M4: 产物预览(洋芋)         │
      │                                                  ├───────────────┤
      │                                                  │ M5: 打磨(全员) │
      │                                                          ├───────────┤
      │                                                          │M6:交付全员│
```

---

## 三、详细任务拆解

### M1：Mock-first 完整闭环（Day 1-4，组长独立）

> **目标：Day 4 结束时，不依赖任何外部 API/CLI，仅用 Mock 就能演示核心流程。**

| # | 任务 | 产出物 | 预估工时 | 优先级 |
|---|------|--------|---------|--------|
| 1.1 | 项目初始化 | monorepo 结构、Vite+React 前端、FastAPI 后端、共享类型包 | 3h | P0 |
| 1.2 | 数据库 Schema 实现 | SQLAlchemy 模型（User/Agent/Conversation/Message/Artifact）+ Alembic 迁移 | 4h | P0 |
| 1.3 | REST API 骨架 | Conversation CRUD + Message CRUD + Agent 列表，含 Pydantic schema | 4h | P0 |
| 1.4 | WebSocket 服务端 | FastAPI WS endpoint，连接管理器，能推送 JSON 事件 | 3h | P0 |
| 1.5 | MockAdapter 实现 | 模拟流式文本 + 代码文件生成 + Diff + TeamNote 事件 | 4h | P0 |
| 1.6 | 前端三栏布局 | Layout 组件、左栏骨架、中栏骨架、右栏占位、路由配置 | 4h | P0 |
| 1.7 | 前端 Zustand Store | conversationStore + messageStore + agentStore + artifactStore | 3h | P0 |
| 1.8 | 前端 WebSocket Hook | useWebSocket 连接/断线重连/事件分发 | 2h | P0 |
| 1.9 | 聊天消息流（基础版） | MessageBubble + 流式文本渲染 + 自动滚动 | 4h | P0 |
| 1.10 | 代码卡片（基础版） | CodeCard 组件（语法高亮占位），能从 Mock 事件渲染 | 2h | P0 |
| 1.11 | Mock 闭环联调 | 前后端联通：发消息 → Mock 流式回复 → 代码卡片展示 | 3h | P0 |

**M1 完成标志：**
- [ ] 前端能新建会话、发送消息
- [ ] MockAdapter 返回流式文本 + 代码卡片
- [ ] 前端能渲染流式消息和代码卡片
- [ ] 不依赖任何外部 API

---

### M2：聊天核心完善（Day 4-8，组长为主 + 小马后端）

> **目标：IM 交互体验达到可演示水平，同时小马开始 Agent 层工作。**

#### 组长负责（前端交互 + Orchestrator）

| # | 任务 | 产出物 | 预估工时 |
|---|------|--------|---------|
| 2.1 | 会话列表完整交互 | ConversationList 搜索/新建/切换/最近消息预览 | 4h |
| 2.2 | 新建对话弹窗 | 选择 Agent、指定项目目录、创建会话 | 3h |
| 2.3 | @ 提及交互 | MentionSelector 浮层，输入 @ 弹出 Agent 列表 | 4h |
| 2.4 | 消息流完善 | 消息时间戳、Agent 头像、角色标识、加载态/骨架屏 | 3h |
| 2.5 | Orchestrator 基础框架 | 后端 OrchestratorService：解析 mentions → 分派 → 汇总 | 5h |
| 2.6 | 预置 Agent 数据 | 数据库 seed：代码工匠/审查大师/文档专家 + 平台绑定 | 1h |

#### 小马负责（Agent Adapter 层）

| # | 任务 | 产出物 | 预估工时 |
|---|------|--------|---------|
| 2.7 | 理解 Adapter 接口 | 阅读 base.py 的 AgentAdapter + TaskContext + AgentEvent | 2h |
| 2.8 | LLMProviderAdapter 实现 | 接入火山方舟 API（OpenAI 兼容格式），流式调用 + 代码块解析 | 6h |
| 2.9 | 火山方舟 API 联调 | 验证 API Key、模型调用、流式输出、错误处理 | 3h |
| 2.10 | Agent 角色 CRUD API | 后端 agents.py：创建/更新/删除自定义 Agent 角色 | 3h |

---

### M3：真实 Agent 接入 + Orchestrator 增强（Day 8-12，小马主导）

> **目标：尝试接入真实 CLI Agent；如果失败则稳定在 LLMProvider。**

#### 小马负责（Agent 接入）

| # | 任务 | 产出物 | 预估工时 |
|---|------|--------|---------|
| 3.1 | OpenCode CLI 调研 | 确认编程接入方式（stdin/API/不可行）、输出格式文档 | 4h |
| 3.2 | OpenCode Adapter 实现（尝试） | 如可行→完整实现 run_task；不可行→记录原因，降级 LLMProvider | 6h |
| 3.3 | Codex CLI 调研 | 确认 full-auto 模式输出格式、进程管理方式 | 4h |
| 3.4 | Codex Adapter 实现（尝试） | 同上 | 6h |
| 3.5 | 进程生命周期管理 | ProcessPool：启动/停止/超时回收/异常重启 | 4h |
| 3.6 | 降级策略实现 | AdapterFactory：health_check → 选择可用 Adapter → 自动降级 | 3h |

#### 组长负责（Orchestrator + Team Protocol）

| # | 任务 | 产出物 | 预估工时 |
|---|------|--------|---------|
| 3.7 | Orchestrator LLM 决策 | 调用火山方舟 API 做意图分析/任务拆解，输出 DispatchPlan JSON | 5h |
| 3.8 | 上下文分层构建 | ContextPayload 四层组装逻辑（项目状态+相关文件+历史+指令） | 4h |
| 3.9 | Team Board 数据结构 | 后端 CRUD + 自动更新逻辑（Agent 完成后 LLM 总结更新） | 4h |
| 3.10 | Project State 维护 | 文件树扫描 + git log 读取 + LLM 摘要 → project_state 表更新 | 3h |
| 3.11 | OrchestratorStatus 推送 | WS 推送任务分派/执行/完成状态 | 2h |

---

### M4：产物与预览系统（Day 8-14，洋芋主导）

> **目标：产物卡片 + 右栏预览面板完整可用。**

#### 洋芋负责

| # | 任务 | 产出物 | 预估工时 |
|---|------|--------|---------|
| 4.1 | File Watcher 服务 | watchdog 监控项目目录，检测文件变更事件 | 4h |
| 4.2 | Diff 计算服务 | 文件变更前后快照 → unified diff → DiffData 结构 | 3h |
| 4.3 | Artifact Service | 根据 AgentEvent(file_created/modified) 生成 Artifact 记录 | 4h |
| 4.4 | Preview Service | FastAPI 静态文件托管 /preview/{conv_id}/* | 3h |
| 4.5 | CodeCard 组件完善 | 语法高亮（highlight.js/Prism）、复制按钮、行号、折叠 | 4h |
| 4.6 | DiffCard 组件 | diff2html 渲染、增删行高亮、摘要统计 | 4h |
| 4.7 | WebPreviewCard 组件 | 聊天流内 iframe 缩略图，点击展开到右栏 | 3h |
| 4.8 | 右栏 PreviewPanel | Tab 切换（预览/代码/Diff）、全屏、关闭、拖拽宽度 | 5h |
| 4.9 | Monaco Editor 集成 | 代码 Tab 中的编辑器，只读模式 + 语法高亮 | 4h |
| 4.10 | Diff Viewer | Monaco Diff Editor 或 diff2html 并排视图 | 3h |

#### 组长协助

| # | 任务 | 产出物 | 预估工时 |
|---|------|--------|---------|
| 4.11 | Artifact WS 推送集成 | 后端 Artifact 生成 → 通过 WS 推送 artifact 事件给前端 | 2h |
| 4.12 | 前端 ArtifactStore 集成 | 收到 artifact 事件 → 更新 store → 卡片自动渲染 | 2h |

---

### M5：体验打磨 + P1 功能（Day 14-17，全员）

> **目标：补全 P1 功能，打磨交互细节，准备 Demo。**

| # | 任务 | 负责人 | 预估工时 |
|---|------|--------|---------|
| 5.1 | Team Activity 卡片 UI | 组长 | 3h |
| 5.2 | Agent Notes 实现（后端注入+前端展示） | 组长 | 4h |
| 5.3 | 群聊 Orchestrator 汇总消息 | 组长 | 3h |
| 5.4 | 自定义 Agent 角色页面 | 小马 | 4h |
| 5.5 | Agent 管理页（平台绑定展示） | 小马 | 3h |
| 5.6 | SkillRule 基础实现 | 小马 | 4h |
| 5.7 | 一键应用 Diff | 洋芋 | 3h |
| 5.8 | 版本历史切换 | 洋芋 | 3h |
| 5.9 | 多文件项目预览 | 洋芋 | 3h |
| 5.10 | 装饰性登录页 | 组长 | 2h |
| 5.11 | 错误处理 + 重试机制 | 全员 | 3h |
| 5.12 | 加载态/空状态/骨架屏 | 全员 | 3h |
| 5.13 | 消息操作（重新生成、复制） | 组长 | 2h |

---

### M6：交付准备（Day 17-20，全员）

> **目标：完成所有交付物，确保 Demo 流畅。**

| # | 任务 | 负责人 | 预估工时 |
|---|------|--------|---------|
| 6.1 | 端到端测试 + Bug 修复 | 全员 | 8h |
| 6.2 | Demo 场景编排（4 个核心场景） | 组长 | 3h |
| 6.3 | Demo 数据准备（预设会话+产物） | 组长 | 2h |
| 6.4 | 3 分钟 Demo 视频录制 | 组长 | 3h |
| 6.5 | 产品设计文档定稿 | 组长 | 2h |
| 6.6 | 技术设计文档定稿 | 小马 + 洋芋 | 2h |
| 6.7 | AI 协作开发记录整理 | 全员 | 2h |
| 6.8 | 部署上线（如有条件） | 洋芋 | 3h |
| 6.9 | 答辩 PPT 准备 | 组长 | 3h |

---

## 四、个人任务汇总

### 组长：架构 + 前端 + Orchestrator（~50% 工作量）

```
Day 1-4:  M1 全部（项目初始化 → Mock 闭环）          ~36h
Day 4-8:  M2 前端交互 + Orchestrator 基础            ~20h
Day 8-12: M3 Orchestrator LLM + Team Protocol       ~18h
Day 8-14: M4 协助 Artifact 集成                      ~4h
Day 14-17: M5 Team Activity + Notes + 登录页 + 打磨  ~14h
Day 17-20: M6 Demo + 文档 + 视频                    ~13h
                                              总计: ~105h
```

**关键交付节点：**
- Day 4：Mock 闭环可演示
- Day 8：聊天核心 + @ 提及可用
- Day 12：Orchestrator 群聊分派可用
- Day 17：全功能可演示

---

### 小马：Agent Adapter + LLM 接入（~25% 工作量）

```
Day 5-8:  M2 LLMProvider + 火山方舟接入              ~14h
Day 8-12: M3 CLI Agent 调研 + 接入/降级              ~27h
Day 14-17: M5 自定义Agent页面 + SkillRule            ~11h
Day 17-20: M6 文档 + 测试                           ~4h
                                              总计: ~56h
```

**关键交付节点：**
- Day 8：LLMProviderAdapter 可用（火山方舟 API 调通）
- Day 12：真实 CLI 接入结论明确（成功/降级）
- Day 17：自定义 Agent 功能可用

**入手指南（Day 5 加入时）：**
1. 阅读 `packages/shared/types.ts` 了解数据契约
2. 阅读 `backend/app/adapters/base.py` 了解接口定义
3. 阅读 `backend/app/adapters/mock.py` 了解参考实现
4. 从 `LLMProviderAdapter.run_task()` 开始编码

---

### 洋芋：产物系统 + 预览能力（~25% 工作量）

```
Day 8-14: M4 全部（File Watcher → 预览 → 卡片组件）  ~37h
Day 14-17: M5 Diff应用 + 版本历史 + 多文件预览        ~9h
Day 17-20: M6 测试 + 部署 + 文档                    ~7h
                                              总计: ~53h
```

**关键交付节点：**
- Day 10：CodeCard + DiffCard 基础版可用
- Day 12：iframe 预览 + Preview 服务可用
- Day 14：右栏 PreviewPanel 完整可用（含 Tab 切换）
- Day 17：版本历史 + 一键应用 Diff 可用

**入手指南（Day 8 加入时）：**
1. 阅读 `packages/shared/types.ts`（重点看 Artifact/DiffData 类型）
2. 阅读 `docs/API_SPEC.md` 第六章（Artifact API）+ 第八章（Preview API）
3. 前端从 `CodeCard.tsx` 组件开始（已有基础版占位）
4. 后端从 `backend/app/services/file_watcher.py` 开始

---

## 五、任务依赖关系

```
M1.5 MockAdapter
  │
  ├──→ M2.8 LLMProviderAdapter（小马参考 Mock 实现）
  │       │
  │       └──→ M3.2 OpenCodeAdapter（在 LLM 基础上尝试 CLI）
  │       └──→ M3.4 CodexAdapter
  │
  ├──→ M4.3 ArtifactService（复用 AgentEvent 定义）
  │
  └──→ M2.5 Orchestrator（先用 Mock 调试分派逻辑）

M1.9 聊天消息流
  │
  ├──→ M2.3 @ 提及交互
  │       │
  │       └──→ M3.7 Orchestrator LLM 决策（@ 触发分派）
  │
  └──→ M4.5-4.7 产物卡片（嵌入消息流中）

M4.4 Preview Service
  │
  └──→ M4.7 WebPreviewCard（需要 preview URL）
         │
         └──→ M4.8 右栏 PreviewPanel
```

**并行安全线：**
- 小马 M2.8 LLMProvider 与 组长 M2.1-2.4 前端交互 → **完全并行**
- 洋芋 M4.1-4.6 产物组件 与 小马 M3.1-3.4 CLI 接入 → **完全并行**
- 组长 M3.7-3.10 Orchestrator 与 洋芋 M4 → **完全并行**

---

## 六、验收检查点

### Day 4 验收（M1 完成）

- [ ] 前后端启动无报错
- [ ] 新建会话 → 发送消息 → Mock 流式回复
- [ ] 代码卡片正确渲染
- [ ] WebSocket 连接稳定

### Day 8 验收（M2 完成）

- [ ] 会话列表交互流畅（新建/切换/搜索）
- [ ] @ 提及弹出 Agent 选择
- [ ] LLMProviderAdapter 成功调用火山方舟 API
- [ ] Agent 流式回复正常显示

### Day 12 验收（M3 完成）

- [ ] 群聊 @ 两个 Agent → Orchestrator 正确分派
- [ ] 分派状态实时推送
- [ ] CLI Agent 接入结论明确（文档记录）
- [ ] Team Board 数据可读取

### Day 14 验收（M4 完成）

- [ ] 代码卡片语法高亮 + 复制
- [ ] Diff 卡片红绿行对比
- [ ] 右栏 iframe 预览网页正确渲染
- [ ] Tab 切换（预览/代码/Diff）

### Day 17 验收（M5 完成）

- [ ] Team Activity 卡片展示在聊天流
- [ ] 自定义 Agent 角色可创建使用
- [ ] 一键应用 Diff
- [ ] 错误态 + 空状态 + 加载态

### Day 20 验收（交付）

- [ ] 4 个 Demo 场景流畅跑通
- [ ] 3 分钟视频完成
- [ ] 产品文档 + 技术文档 + AI 协作记录齐全

---

## 七、风险缓冲

| 风险场景 | 缓冲方案 |
|---------|---------|
| 组长 M1 延期 1-2 天 | M2 相应后移，但 Mock 闭环必须在 Day 6 前完成 |
| 小马火山方舟 API 未到 | 先用 OpenAI/DeepSeek API 开发 LLMProvider，接口一致切换无成本 |
| 洋芋 Day 8 无法全力投入 | 组长先做 CodeCard 基础版（已在 M1 完成），洋芋只做增强 |
| CLI Agent 全部接入失败 | LLMProvider 作为正式方案，Demo 效果几乎一致 |
| M5 时间不够 | 砍 SkillRule（P1）和版本历史（P1），保住 Team Activity（P0） |

---

*任务拆解文档 v1.0 — 20 天 MVP，组长先行建框架，小马/洋芋接力填充。*
