# M2 UI Polish Plan

## Goal

把 M2 工作台从基础可用界面优化为接近参考图的高完成度桌面端界面：三栏 IM 协作工作台、成熟聊天卡片、产物卡片，以及 `产出物 | 预览 | 变更` 右侧工作台。

## Scope

- 仅修改前端视觉和现有前端派生状态。
- 保留当前 REST/WebSocket 数据流、Zustand store、MockAdapter 闭环。
- 右侧预览不依赖后端 `/preview`，先使用 artifact HTML 内容生成 `iframe srcDoc`。
- 顶部状态只展示现有前端可直接派生的信息：参与 Agent、参与数量、WebSocket 状态、Orchestrator runtime 状态。

## Contract Notes

- 不修改 `packages/shared/types.ts`。
- 不修改 `docs/API_SPEC.md`。
- 不新增后端路由或 WebSocket 消息类型。
- 不展示真实“在线人数”或平台健康状态，避免伪造后端未提供的 presence 数据。

## Target Files

- `frontend/src/index.css`：全局视觉系统、三栏布局、卡片、输入区、预览区样式。
- `frontend/src/components/common/Layout.tsx`：保留三栏骨架，增加语义类名即可。
- `frontend/src/components/chat/ConversationList.tsx`：重塑左侧品牌区、主按钮、Agent 卡、会话卡。
- `frontend/src/components/chat/ChatArea.tsx`：优化顶部标题区、参与 Agent chip、协作状态、消息区结构。
- `frontend/src/components/chat/MessageBubble.tsx`：优化用户/Agent 消息卡片、时间、身份标签和产物区域。
- `frontend/src/components/chat/MessageInput.tsx`：优化输入框、快捷按钮和发送按钮布局。
- `frontend/src/components/cards/CodeCard.tsx`：把代码块式卡片改为文件产物卡。
- `frontend/src/components/preview/PreviewPanel.tsx`：实现 `产出物 | 预览 | 变更` 三 Tab，产出物列表、iframe srcDoc 预览、变更占位。

## Implementation Steps

1. 更新计划和 checklist。
2. 重塑全局 CSS：颜色、间距、边框、三栏比例、滚动区域、按钮和卡片基础样式。
3. 重写左侧栏视觉：Logo、橙色新建按钮、搜索框、常用代理、对话列表、底部设置入口。
4. 重写聊天顶部：标题、编辑图标、参与 Agent chip、派生协作状态。
5. 重写消息卡片和产物卡片：参考图中的白色卡片、文件行、状态与预览按钮。
6. 重写输入区：大输入框、`@ 代理` / `/ 命令` / `附件` 快捷按钮、橙色发送按钮。
7. 重写 PreviewPanel：三 Tab、文件列表、srcDoc iframe 预览、变更占位。
8. 运行 `npm run lint` 和 `npm run build`。
9. 用浏览器打开 `http://localhost:5173/workspace` 做桌面端视觉烟测。
10. 更新 checklist 和 `DEVLOG.md`。

## Tests

- `cd frontend && npm run lint`
- `cd frontend && npm run build`
- 浏览器烟测：
  - 工作台能打开。
  - 左侧 Agent、会话列表正常渲染。
  - 发送 Mock 消息后聊天卡片和产物卡片正常展示。
  - 右侧 `产出物 | 预览 | 变更` 可切换。
  - HTML artifact 在 `预览` Tab 中以 iframe 渲染。

## Out of Scope

- 不实现真实 LLM/OpenCode/Codex Adapter。
- 不实现后端 Preview Service。
- 不实现真实在线人数、平台健康检查、多人 presence。
- 不新增移动端完整适配。
- 不引入新的 npm 依赖。
