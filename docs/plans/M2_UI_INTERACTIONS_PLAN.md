# M2 UI Interactions Plan

## Goal

补齐 M2 UI polish 后立即可实现的前端交互，并把暂不适合当前阶段实现的按钮功能登记为技术债，避免界面出现无反馈入口。

## Scope

- 实现右侧预览区桌面/平板/手机视口切换。
- 实现右侧预览区缩放 `- / +`。
- 将聊天顶部参与数量、时钟图标弱化为只读状态文本，并实时更新时间。
- 保留 `+ 添加代理` chip 作为未来自定义 Agent/参与者管理入口。
- 记录尚未实现按钮的预期功能和建议实现阶段。

## Contract Notes

- 不修改后端接口。
- 不修改 WebSocket 消息类型。
- 不修改 `packages/shared/types.ts`。
- 所有新增状态仅在前端组件内派生。

## Target Files

- `frontend/src/components/chat/ChatArea.tsx`
- `frontend/src/components/preview/PreviewPanel.tsx`
- `frontend/src/index.css`
- `docs/TECH_DEBT.md`
- `docs/plans/M2_UI_INTERACTIONS_CHECKLIST.md`
- `DEVLOG.md`

## Implementation Steps

1. 新增 plan/checklist。
2. 新增/更新 `docs/TECH_DEBT.md`，记录未实现按钮和预期功能。
3. 在 `ChatArea` 中增加本地分钟级时钟，并把参与数量/更新时间渲染为只读文本。
4. 在 `PreviewPanel` 中增加 `viewport` 与 `zoom` 状态。
5. 把桌面/平板/手机图标改成真实按钮，点击后切换 iframe 容器宽度。
6. 把 `- / +` 缩放按钮接到 zoom 状态，限制范围为 75%-125%。
7. 更新 CSS，提供 active 状态、不同 viewport 宽度、缩放 transform。
8. 运行 `npm run lint`、`npm run build`。
9. 浏览器烟测：打开工作台，切换预览设备和缩放，确认无 console error。

## Tests

- `cd frontend && npm run lint`
- `cd frontend && npm run build`
- 浏览器烟测：
  - 聊天顶部显示“X 个代理参与”和更新时间文本。
  - 预览区桌面/平板/手机按钮可切换 active 状态。
  - 预览区 `- / +` 会更新缩放百分比。

## Out of Scope

- 不实现编辑会话标题。
- 不实现添加代理/自定义 Agent。
- 不实现设置页完整功能。
- 不实现命令面板、附件上传、发送菜单。
- 不实现全屏预览和文件选择下拉。
