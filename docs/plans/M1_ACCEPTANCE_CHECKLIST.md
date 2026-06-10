# M1 Mock-first 完整闭环验收 Checklist

## 阶段完成

- [x] M1_1 后端数据与 REST 基线完成。
- [x] M1_2 WebSocket + MockAdapter 流式闭环完成。
- [x] M1_3 前端工作台基础壳完成。
- [x] M1_4 聊天流 + 代码卡片 + 全链路联调完成。

## 自动化验证

- [x] `cd backend && pytest -q` 通过。
- [x] `cd frontend && npm run build` 通过。
- [x] Skill 校验通过：`nailaude-module-development` 有效。

## 浏览器验收

- [x] 前端工作台可打开。
- [x] Agent 列表可加载。
- [x] 可新建 Mock 会话。
- [x] WebSocket 状态可变为 `open`。
- [x] 可发送用户消息。
- [x] 可显示 Mock Agent 流式回复。
- [x] 可显示 `index.html` 代码卡片。
- [x] 右侧 PreviewPanel 可显示 active artifact 摘要。

## M1 完成标准

- [x] 前后端启动无报错。
- [x] 前端能新建会话、发送消息。
- [x] MockAdapter 返回流式文本和代码产物。
- [x] 前端能渲染流式消息和代码卡片。
- [x] WebSocket 连接稳定。
- [x] 全流程不依赖外部 API/CLI。
