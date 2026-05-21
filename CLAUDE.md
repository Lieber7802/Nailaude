# CLAUDE.md — Claude Code 会话上下文

> Claude Code 每次启动会自动加载此文件。

## 必读文件

开始工作前，按需阅读以下文件获取上下文：

- `AGENTS.md` — AI 编码规则、项目结构、核心概念（**必读**）
- `DEVLOG.md` — 最近的开发进展（读最近 3-5 条即可了解当前状态）
- `packages/shared/types.ts` — 类型契约（修改 API 相关代码前必读）
- `docs/API_SPEC.md` — API 规范（写后端路由或前端请求时参考）

## 会话规则

1. **开始时**：说明你要做什么任务（对应 TASK_BREAKDOWN 中的哪个编号）
2. **编码中**：遵循 AGENTS.md 中的编码规则
3. **结束时**：在 DEVLOG.md 末尾追加一条会话记录（格式见 DEVLOG.md 顶部说明）

## 快速命令

```bash
# 启动后端
cd backend && uvicorn app.main:app --reload --port 8000

# 启动前端
cd frontend && npm run dev

# 数据库迁移
cd backend && alembic upgrade head
```

## 当前阶段

查看 `DEVLOG.md` 最后一条了解项目当前进度。
