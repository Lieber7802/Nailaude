# nailaude AI 协作开发流程说明

## 1. 流程背景

nailaude 本身是一个多 Agent 协作系统，开发过程中也大量使用 AI 参与架构设计、代码实现、问题分析、测试补齐和文档整理。因此，项目不能只依赖临时对话来驱动开发，而需要一套稳定的协作流程来约束 AI 的行为。

如果没有明确流程，AI 辅助开发容易出现几个问题：改动范围扩大、接口契约不一致、没有真实验证就声称完成、历史决策无法交接、同类 bug 反复出现。nailaude 通过文档、契约、计划、测试和 DEVLOG，把 AI 的参与过程从“临场发挥”变成可追踪、可复现的工程流程。

## 2. AI 协作开发总流程

项目采用的标准流程如下：

```text
接收任务
  |
  v
读取项目契约
  |
  v
创建/更新 plan 和 checklist
  |
  v
测试先行或确认验证方式
  |
  v
按模块边界实现
  |
  v
运行目标测试和必要烟测
  |
  v
更新 checklist 和 DEVLOG
  |
  v
总结交接
```

这套流程的核心目标是让 AI 每一步都有依据：先理解项目上下文，再明确修改范围，然后通过测试验证，最后沉淀给后续开发者和后续 AI 助手。

## 3. AI 的工作依据

AI 参与项目时，需要先知道“项目是什么、边界在哪里、按什么流程做、怎样证明完成”。nailaude 把这些信息拆到几类固定材料中：

| 材料 | 主要作用 |
|------|----------|
| `AGENTS.md` | 提供项目目标、模块边界、核心概念和禁止事项 |
| 项目级 skill | 把本项目标准工作流固化成 AI 可重复执行的步骤 |
| `docs/API_SPEC.md` / `packages/shared/types.ts` | 约束 API、WebSocket 和共享数据结构 |
| `docs/plans/*` | 记录模块目标、实现范围、任务拆解和验证方式 |
| `DEVLOG.md` | 沉淀每次 AI 协作开发的事实和验证结果 |

### 3.1 项目入口说明

`AGENTS.md` 是 AI 助手进入项目后的第一份说明。它告诉 AI：

- 项目目标是什么，不是什么。
- 前后端、后端 service、adapter、shared types、docs 的职责边界。
- Agent、Conversation、Message、Artifact、Orchestrator、TeamBoard 等核心概念。
- 修改代码前需要先读哪些契约。
- 哪些行为被禁止，例如删除 MockAdapter、修改密钥、暴露底层 platformId、顺手做 P2 功能。

这份文件相当于项目地图，避免 AI 只看局部代码就开始猜测。

### 3.2 自定义项目 skill

除了系统本身提供的一些通用 skill，我们还根据 nailaude 的开发标准工作流，自定义了项目级 skill：`.agents/skills/agenthub-module-development/SKILL.md`。

这个 skill 不是凭空生成的，而是把项目已有规则固化为可重复执行的流程：先读契约、定义模块边界、创建计划和 checklist、测试先行、遵守 Mock-first 和模块职责、运行验证、更新 DEVLOG。这样不同 AI 助手在参与 AgentHub/nailaude 开发时，不需要重新理解一遍协作方式，而是可以直接沿着同一套工作流推进。

### 3.3 契约文档

`docs/API_SPEC.md` 和 `packages/shared/types.ts` 是前后端共同契约。涉及 API、WebSocket、前端 service、Adapter 或共享数据结构的改动，都必须先对齐这两份文件。

这种 contract-first 方式解决的是多人和多 AI 协作中的典型问题：一个地方改了字段，另一个地方仍按旧结构使用。通过共享类型和 API 文档，AI 的修改不会只在单个文件里自洽，而是要和系统整体一致。

### 3.4 模块计划

`docs/plans/` 下的 plan 和 checklist 用来拆解模块任务。计划记录目标、范围、契约影响、实现步骤和测试方式；checklist 把任务拆成可验证的完成项。

对 AI 来说，这些文件的价值是降低任务模糊度。它们让 AI 知道这次要改什么、不改什么、如何证明完成，也让后续协作者能接上前一次开发的上下文。

## 4. 边界、验证与记录

nailaude 对 AI 的约束不是单一规则，而是由三层机制共同完成。

第一层是模块边界。前端负责 UI 和交互，后端 API 负责路由和参数校验，后端 service 负责业务逻辑，adapter 只负责平台接入，shared types 只放契约。AI 修改代码时必须尊重这些边界，避免把业务判断写进 adapter，或把文件系统操作放到前端。

第二层是可验证实现。项目强调 Mock-first 和 Test-first。MockAdapter 是永久兜底能力，让系统在没有外部 API 或 CLI 时仍能开发和测试；行为变化和 bug 修复优先写回归测试，避免“看起来修了但无法证明”。

第三层是确定性校验。对于 LLM 输出，项目不会完全依赖模型自觉，而是通过 Pydantic schema、PlanValidator、任务依赖校验、agent 参与者校验等方式，把语义规划放进明确边界里。LLM 负责提出方案，后端负责判断方案是否合法。

每次完成后，AI 还必须更新 DEVLOG，记录问题判断、修改文件、接口影响和验证命令。这样 AI 的工作不会停留在聊天窗口中，而是进入项目历史。

## 5. Agent 友好设计

nailaude 的 Agent 友好体现在两个层面。

在开发层面，项目给 AI 提供了清晰的入口和上下文：`AGENTS.md` 说明项目规则，shared types 和 API spec 提供契约，plans/checklists 拆解任务，DEVLOG 记录历史决策和验证结果。AI 不需要从零猜项目结构，也不需要依赖完整聊天记录理解当前状态。

在产品运行层面，系统也为运行时智能体提供结构化协作条件。每个 Agent 有能力标签和 system instruction，Orchestrator 根据参与者和任务目标分配工作；子智能体执行前会收到任务目标、验收标准、项目摘要、团队规范、前序任务结果和相关便签；产出结果会被转成 Artifact、Team Note、Project State 更新，再反馈给后续任务。

这使得 Agent 既容易参与项目开发，也容易在 nailaude 产品中作为协作角色稳定工作。

## 6. AI 在项目中的作用

AI 在 nailaude 开发中承担了多种工作，但不是无边界地“自动写项目”。它主要参与架构讨论、模块实现、问题分析、回归测试补齐、文档整理和代码审查式分析。

例如 Orchestrator、Adapter、Team Protocol、Project State、Artifact Preview 等模块，都通过“先计划、再实现、再验证、再记录”的方式推进。遇到问题时，AI 需要先定位链路和原因，再写测试或给出可验证修复，而不是直接改一大片代码。

因此 AI 在本项目中的角色更接近“受约束的协作开发者”，而不是一次性代码生成器。

## 7. DEVLOG 作为协作开发记录

`DEVLOG.md` 是本项目的详细 AI 协作开发记录。它比普通 changelog 更适合说明 AI 协作过程，因为它不只记录改了什么，还记录为什么改、影响哪些文件、是否涉及接口变化、运行了哪些验证、还有什么注意事项。

项目复盘或展示时，DEVLOG 可以作为原始开发记录；本文档则解释这些记录背后的协作方法。两者关系是：

- `DEVLOG.md`：按时间记录每次 AI 协作开发事实。
- `AI_COLLABORATION_PROCESS.md`：总结项目如何组织、约束和复用 AI 协作。
- `docs/plans/*`：展示每个模块如何被拆成可执行计划。
- `AGENTS.md`：展示项目如何给 AI 助手提供入口规则。

## 8. 可复用经验

nailaude 的 AI 协作经验可以概括为：

1. 先给 AI 项目地图，再让 AI 改代码。
2. 跨端接口必须有共享契约。
3. 复杂任务先拆成计划和 checklist。
4. Mock 是稳定协作的基础设施，不是临时假数据。
5. 对 LLM 输出要有 schema 和确定性校验。
6. 测试结果必须真实、具体、可复现。
7. DEVLOG 是团队和 AI 的共同记忆。

## 9. 总结

nailaude 的 AI 协作开发流程可以概括为：

> 用文档给 AI 上下文，用契约限制 AI 输出，用计划拆小任务，用测试确认行为，用 DEVLOG 保留团队记忆。

这套流程既支撑了项目本身的开发，也与 nailaude 的产品理念一致：让智能体在清晰边界、共享上下文和可验证状态下协作完成复杂任务。
