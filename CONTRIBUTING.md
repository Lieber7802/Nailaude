# CONTRIBUTING — 协作开发规范

> 三人团队 + AI 编码助手的协作规范。

---

## Git 分支策略

```
main              # 稳定版本，Demo/交付时从 dev 合入
└── dev           # 开发主线，三人的 feature 分支合入此处
    ├── feat/xxx  # 功能分支
    ├── fix/xxx   # 修复分支
    └── refactor/xxx  # 重构分支
```

### 分支命名

```
feat/mock-adapter       # 新功能
feat/chat-message-flow
fix/ws-reconnect        # Bug 修复
refactor/store-cleanup  # 重构
```

### 工作流程

1. 从 `dev` 拉取最新代码
2. 创建 feature 分支
3. 开发 + 提交（小步提交）
4. 推送到远程，创建 PR 到 `dev`
5. PR 描述中说明改动内容和影响范围
6. 合入后在 DEVLOG.md 追加记录

---

## Commit Message 格式

```
类型(模块): 一句话描述

- 改动详情 1
- 改动详情 2

影响: 受影响的模块
关联: TASK_BREAKDOWN 任务编号（如 M1.5）
```

### 类型

| 类型 | 用途 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `refactor` | 重构（不改功能） |
| `docs` | 文档更新 |
| `style` | 代码格式（不改逻辑） |
| `chore` | 构建/工具/依赖 |

### 示例

```
feat(adapter): implement LLMProviderAdapter with volcano API

- 新增 backend/app/adapters/llm_provider.py
- 支持 OpenAI 兼容格式流式调用
- 代码块解析后写入项目目录

影响: backend/adapters
关联: M2.8
```

---

## PR 模板

创建 PR 时使用以下格式：

```markdown
## 改动内容
<!-- 做了什么，1-3 句 -->

## 影响范围
<!-- 哪些模块受影响 -->
- [ ] frontend
- [ ] backend/api
- [ ] backend/services
- [ ] backend/adapters
- [ ] packages/shared
- [ ] docs

## 契约变更
<!-- 是否修改了以下文件 -->
- [ ] packages/shared/types.ts
- [ ] docs/API_SPEC.md

## 测试方式
<!-- 如何验证改动正确 -->

## 关联任务
<!-- TASK_BREAKDOWN 中的编号 -->
```

---

## 契约文件修改规则

以下文件是三人共享的接口契约，修改前需通知团队：

| 文件 | 规则 |
|------|------|
| `packages/shared/types.ts` | 修改后同步更新 API_SPEC.md，PR 中标注 `⚠️ 契约变更` |
| `docs/API_SPEC.md` | 修改后确认 types.ts 是否需要同步 |
| `backend/app/adapters/base.py` | 修改接口影响所有 Adapter，需通知小马 |

---

## 会话沉淀规则

每次 AI 编码会话结束时：

1. 在 `DEVLOG.md` 末尾追加记录（格式见 DEVLOG.md 顶部）
2. 如果有契约变更，在记录中标注 `⚠️`
3. 如果有给其他成员的提醒，用 `@成员名` 标注

---

## 代码规范

### 前端

- 使用函数组件 + Hooks
- 组件文件 PascalCase：`ChatArea.tsx`
- Store 文件 camelCase：`messageStore.ts`
- 使用 `shared/types.ts` 中的类型，不在前端重复定义
- CSS 方案：Ant Design 组件 + Tailwind utility（如果引入）

### 后端

- 路由文件只做参数校验和调用 Service，不含业务逻辑
- Service 层处理核心逻辑
- Adapter 层只关注 Agent 通信，不含业务判断
- 异步优先（async/await）
- 类型注解完整

---

## 冲突处理

如果两人改了同一文件产生冲突：

1. 优先保留更底层的改动（类型定义 > 接口 > 实现）
2. 如果是 UI 组件冲突，以最新的设计为准
3. 如果不确定，在群里沟通后再合并
