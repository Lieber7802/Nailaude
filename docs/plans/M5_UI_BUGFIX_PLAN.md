# M5 UI Bugfix Plan

## Goal

修复左侧会话列表时间、侧边栏自定义智能体入口、聊天产物列表默认折叠、协作状态失败/阻塞样式与智能体耗时展示问题。

## Scope

- 前端会话列表展示逻辑与按钮布局。
- 聊天消息内产物卡片默认展示前 5 个，其余折叠并支持展开/收起。
- 协作状态卡片按智能体任务状态展示不同 tone，并显示本地运行态耗时。
- 相关纯逻辑测试、样式与 DEVLOG。

## Contract Notes

- `Conversation.updatedAt` 是左侧列表最近活跃排序和时间展示来源，缺失时回退 `createdAt`。
- `Task.status` 已包含 `completed`、`failed`、`blocked`、`cancelled`，本次不修改共享类型。
- 当前 `Task` 契约无精确耗时字段，前端运行态本地记录智能体开始/结束时间用于展示耗时。
- 不修改 REST、WebSocket payload 或后端实现。

## Implementation Steps

1. 新增/扩展前端工具函数，格式化会话列表时间、产物折叠结果、协作智能体 tone 与耗时。
2. 调整 `ConversationList`，将自定义智能体按钮移动到新建对话按钮下方并使用同尺寸按钮。
3. 调整 `MessageBubble`，默认只渲染前 5 个产物并提供展开/收起按钮。
4. 扩展 `uiStore` 运行态，记录智能体 thinking/task 执行耗时。
5. 调整 `RuntimeBanner` 与 CSS，区分 pending/done/danger/warning/idle 状态样式并显示耗时。

## Tests

- `frontend/tests/chatUi.test.mjs` 覆盖会话列表时间格式化。
- `frontend/tests/artifactCard.test.mjs` 覆盖产物默认 5 个折叠与展开。
- `frontend/tests/orchestratorUi.test.mjs` 覆盖失败/阻塞 tone 和耗时展示。
- 运行 `cd frontend && npm test` 和 `cd frontend && npm run build`。

## Out of Scope

- 不新增后端耗时字段。
- 不调整 MockAdapter 或真实 Adapter 行为。
- 不实现移动端或 P2 功能。
