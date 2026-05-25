# M1_3 前端工作台基础壳 Checklist

## Docs

- [x] `docs/plans/M1_3_PLAN.md` 已创建。
- [x] `docs/plans/M1_3_CHECKLIST.md` 已创建。

## Implementation

- [x] API client 支持统一 `ApiResponse<T>`。
- [x] Agent API 可加载列表。
- [x] Conversation API 可加载/创建/删除。
- [x] Message API 可加载历史。
- [x] Conversation store 支持 set/list/add/active。
- [x] Message store 支持 set/append stream/finalize。
- [x] Agent store 支持加载列表。
- [x] Artifact store 支持添加和选中。
- [x] WebSocket client 支持连接、断开、发送、订阅、状态回调。
- [x] `useWebSocket` 能把 WS 事件写入 store。
- [x] Workspace 显示三栏基础壳。

## Verification

- [x] `cd frontend && npm run build` 通过。
- [x] `DEVLOG.md` 已追加记录。
