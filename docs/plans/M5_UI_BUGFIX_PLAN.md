# M5 UI Bugfix Plan

## Goal

修复左侧会话列表时间、侧边栏自定义智能体入口、聊天产物列表默认折叠、协作状态失败/阻塞样式与智能体耗时展示、刷新后计时准确性与左侧搜索误用问题。

## Scope

- 前端会话列表展示逻辑与按钮布局。
- 聊天消息内产物卡片默认展示前 5 个，其余折叠并支持展开/收起。
- 协作状态卡片按智能体任务状态展示不同 tone，并显示后端权威耗时。
- 右侧预览底部 viewport 切换按钮在窄面板下自动隐藏文字标签，避免中文标签被挤成竖排。
- 右侧预览底部缩放条根据窗格宽度自动收缩，避免 range slider 在窄面板下被裁切。
- 右侧预览底部缩放控件在宽面板下保持紧凑宽度，避免无意义空白。
- 左侧栏对话列表在内容超过可视高度时保持独立纵向滚动，避免被外层裁切。
- 工作台空状态和右侧空预览不暴露 Mock / unsupported 这类实现细节。
- 右侧全屏 Markdown 预览铺满可用空间。
- 刷新后的终态任务不重新生成本地耗时计时。
- 后端 runtime 在任务快照里写入 `startedAt` / `endedAt`，前端只基于该字段展示耗时。
- 移除左侧搜索对话/消息入口和搜索触发逻辑。
- 修复左侧对话列表在剩余空间较多时把少量会话项纵向拉伸成大卡片的问题。
- 自定义智能体管理页支持查看、创建和删除自定义智能体。
- 相关纯逻辑测试、样式与 DEVLOG。

## Contract Notes

- `Conversation.updatedAt` 是左侧列表最近活跃排序和时间展示来源，缺失时回退 `createdAt`。
- `Task.status` 已包含 `completed`、`failed`、`blocked`、`cancelled`。
- `Task.startedAt` / `Task.endedAt` 为后端权威任务计时字段，随 `orchestrator_status.tasks[]` 推送。
- 左侧列表仍通过 `GET /conversations?page=1&pageSize=20` 拉取；本轮仅删除前端搜索 UI，不删除后端兼容参数。

## Implementation Steps

1. 新增/扩展前端工具函数，格式化会话列表时间、产物折叠结果、协作智能体 tone 与耗时。
2. 调整 `ConversationList`，将自定义智能体按钮移动到新建对话按钮下方并使用同尺寸按钮。
3. 调整 `MessageBubble`，默认只渲染前 5 个产物并提供展开/收起按钮。
4. 扩展 `uiStore` 运行态，记录智能体 thinking/task 执行耗时。
5. 调整 `RuntimeBanner` 与 CSS，区分 pending/done/danger/warning/idle 状态样式并显示耗时。
6. 调整预览 viewport 切换按钮响应式样式，窄宽时隐藏文字，仅保留图标。
7. 调整预览缩放控件 flex 行为，使用容器剩余空间而非 viewport 宽度计算 slider。
8. 限制预览缩放控件最大宽度，防止宽窗格下被拉伸出空白区域。
9. 修复左侧栏对话列表的 flex 高度约束，让滚动容器占满剩余空间并产生内部滚动。
10. 调整工作台和预览空状态文案，避免暴露实现细节。
11. 调整 Markdown 预览全屏样式，让正文容器铺满预览面板。
12. 调整 runtime 计时逻辑，终态任务只有后端开始时间时才展示耗时。
13. 实现自定义智能体管理页，复用创建弹窗并接入删除 API。
14. 在后端 Orchestrator runtime 为任务写入 `startedAt` / `endedAt`。
15. 删除左侧搜索框、搜索 state、debounced search 请求。
16. 设置 `.conversation-list` 的 grid 内容从顶部开始排列，隐式行按内容高度生成。

## Tests

- `frontend/tests/chatUi.test.mjs` 覆盖会话列表时间格式化。
- `frontend/tests/artifactCard.test.mjs` 覆盖产物默认 5 个折叠与展开。
- `frontend/tests/orchestratorUi.test.mjs` 覆盖失败/阻塞 tone 和耗时展示。
- `frontend/tests/previewControls.test.mjs` 覆盖 viewport 标签隐藏断点配置。
- `frontend/tests/previewControls.test.mjs` 覆盖缩放 slider 窄宽最小宽度配置。
- `frontend/tests/previewControls.test.mjs` 覆盖缩放控件宽窗格最大紧凑宽度配置。
- `frontend/tests/sidebarLayout.test.mjs` 覆盖左侧栏对话列表滚动容器的 flex 高度约束。
- `frontend/tests/experiencePolish.test.mjs` 覆盖空状态文案、Markdown 全屏样式和自定义智能体管理页能力。
- `frontend/tests/runtimeStore.test.mjs` 覆盖刷新后终态任务不凭空生成耗时。
- `backend/tests/test_m3_orchestrator_runtime.py` 覆盖后端任务权威开始/结束时间。
- `frontend/tests/runtimeStore.test.mjs` 覆盖前端使用后端任务时间字段。
- `frontend/tests/sidebarLayout.test.mjs` 覆盖左侧搜索移除。
- `frontend/tests/sidebarLayout.test.mjs` 覆盖对话列表额外空间不拉伸会话行。
- 运行 `cd frontend && npm test` 和 `cd frontend && npm run build`。
- 运行 `cd backend && .venv/bin/python -m pytest tests/test_m3_orchestrator_runtime.py tests/test_m4_artifact_preview.py`。

## Out of Scope

- 不调整 MockAdapter 或真实 Adapter 行为。
- 不实现移动端或 P2 功能。
