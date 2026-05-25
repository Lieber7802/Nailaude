# M1_2 WebSocket + MockAdapter 流式闭环 Checklist

## Docs

- [x] `docs/plans/M1_2_PLAN.md` 已创建。
- [x] `docs/plans/M1_2_CHECKLIST.md` 已创建。

## Tests

- [x] WS 完整 Mock 事件流测试已先写。
- [x] 缺失 conversation 的 WS 错误测试已先写。
- [x] 后端测试通过。

## Implementation

- [x] MockAdapter 输出 `text_delta`、`file_created`、`team_note`、`done`。
- [x] WS handler 支持 `send_message`。
- [x] WS handler 不再 echo 普通消息。
- [x] 用户消息通过 WS 持久化。
- [x] Agent 消息通过 WS 持久化。
- [x] `file_created` 转为 Artifact 记录。
- [x] WS 推送 `agent_thinking`。
- [x] WS 推送 `text_delta`。
- [x] WS 推送 `artifact`。
- [x] WS 推送 `team_activity`。
- [x] WS 推送 `message_done`。
- [x] WS 推送统一 `error` 消息。

## Verification

- [x] `cd backend && pytest -q` 通过。
- [x] M1_2 checklist 已更新。
- [x] `DEVLOG.md` 已追加记录。
