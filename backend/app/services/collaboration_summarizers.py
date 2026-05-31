"""DeepSeek-backed summarizers for compact collaboration state."""
from __future__ import annotations

from app.services.llm_client import LLMClient


class ProjectStateSummarizer:
    def __init__(self, client: LLMClient | None = None):
        self.client = client or LLMClient()

    async def __call__(self, state, task_results: list[dict]) -> str:
        result = await self.client.request_json(
            [
                {
                    "role": "system",
                    "content": "Summarize project progress as JSON with one concise summary string. Do not invent facts.",
                },
                {
                    "role": "user",
                    "content": str(
                        {
                            "workspace": state.workspace,
                            "fileTree": state.file_tree,
                            "git": state.git,
                            "previousSummary": state.progress_summary,
                            "taskResults": task_results,
                        }
                    ),
                },
            ]
        )
        return str(result.content.get("summary") or "").strip()


class TeamBoardSummarizer:
    def __init__(self, client: LLMClient | None = None):
        self.client = client or LLMClient()

    async def __call__(self, board, task_results: list[dict]) -> dict:
        result = await self.client.request_json(
            [
                {
                    "role": "system",
                    "content": (
                        "Return a JSON Team Board patch. Only use currentFocus and openQuestions. "
                        "Do not rewrite deterministic progress, decisions, or standards."
                    ),
                },
                {
                    "role": "user",
                    "content": str(
                        {
                            "progress": board.progress,
                            "openQuestions": board.open_questions,
                            "recentNotes": board.recent_notes,
                            "taskResults": task_results,
                        }
                    ),
                },
            ]
        )
        return dict(result.content)
