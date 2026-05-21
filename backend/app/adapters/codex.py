"""
Codex Adapter - Integration with OpenAI Codex CLI.

Codex uses a one-shot task model (one process per task).
run_task() spawns a new process each time.
"""
from typing import AsyncGenerator

from app.adapters.base import AgentAdapter, AgentEvent


class CodexAdapter(AgentAdapter):
    """Codex CLI adapter - one-shot task execution."""

    platform_name = "codex"

    async def run_task(
        self, work_dir: str, instruction: str, context: dict
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Execute task via Codex CLI (new process per task).
        TODO: Implement subprocess spawn and output streaming
        """
        yield AgentEvent(type="text_delta", content="[Codex not implemented]")
        yield AgentEvent(type="done", content="")

    async def health_check(self) -> bool:
        # TODO: check if codex binary exists
        return False
