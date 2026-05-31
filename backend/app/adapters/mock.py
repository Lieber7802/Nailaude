"""
MockAdapter - Permanent mock adapter for development, testing, and demo fallback.

This adapter simulates agent behavior without any external dependencies.
It is NOT a temporary component - it stays in production as a fallback.
"""
import asyncio
from pathlib import Path
from typing import AsyncGenerator
import uuid

from app.adapters.base import AgentAdapter, AgentEvent


class MockAdapter(AgentAdapter):
    """Mock Agent adapter - simulates streaming text and artifact generation."""

    platform_name = "mock"

    def __init__(self, response_delay: float = 0.05):
        self.response_delay = response_delay

    async def run_task(
        self, work_dir: str, instruction: str, context: dict
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Simulate a task execution with streaming text, a code artifact, and a team note.
        """
        chunks = [
            "Mock 已生成一个基础页面。",
            " 下面是可预览的 HTML 产物。",
        ]
        for chunk in chunks:
            if self.response_delay:
                await asyncio.sleep(self.response_delay)
            yield AgentEvent(type="text_delta", content=chunk)

        generation_id = str(uuid.uuid4())
        html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AgentHub Mock Page</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 0; padding: 48px; background: #f7f8fa; color: #1f2329; }
    main { max-width: 720px; margin: 0 auto; background: white; border: 1px solid #e5e6eb; border-radius: 8px; padding: 32px; }
    button { border: 0; border-radius: 6px; background: #1677ff; color: white; padding: 10px 16px; }
  </style>
</head>
<body>
  <!-- mock-generation: MOCK_GENERATION_ID -->
  <main>
    <h1>AgentHub Mock 页面</h1>
    <p>这是 MockAdapter 为当前任务生成的演示产物。</p>
    <button>开始体验</button>
  </main>
</body>
</html>
""".replace("MOCK_GENERATION_ID", generation_id)
        if (context.get("workspace") or {}).get("accessMode") == "write":
            workspace = Path(work_dir)
            workspace.mkdir(parents=True, exist_ok=True)
            Path(workspace, "index.html").write_text(html, encoding="utf-8")
        yield AgentEvent(
            type="file_created",
            content="index.html",
            metadata={
                "title": "index.html",
                "files": [{"name": "index.html", "content": html, "language": "html"}],
                "previewUrl": None,
            },
        )
        yield AgentEvent(
            type="team_note",
            content="MockAdapter 已生成基础 HTML 产物，可交给前端渲染代码卡片。",
            metadata={"fromAgent": context.get("agentName", "代码工匠"), "to": "all", "noteType": "decision"},
        )
        yield AgentEvent(type="done", content="")

    async def health_check(self) -> bool:
        return True
