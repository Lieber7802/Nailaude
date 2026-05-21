"""
LLM Provider Adapter - OpenAI-compatible API direct call.

Uses Volcano Engine / DeepSeek / OpenAI API with streaming.
Parses code blocks from LLM output and writes to project directory.
"""
from typing import AsyncGenerator

from app.adapters.base import AgentAdapter, AgentEvent


class LLMProviderAdapter(AgentAdapter):
    """LLM Provider adapter - direct API call with code extraction."""

    platform_name = "llm_provider"

    async def run_task(
        self, work_dir: str, instruction: str, context: dict
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Call LLM API, stream response, extract code blocks.
        TODO: Implement actual API call with httpx
        """
        yield AgentEvent(type="text_delta", content="[LLM Provider not implemented]")
        yield AgentEvent(type="done", content="")

    async def health_check(self) -> bool:
        # TODO: check API key validity
        return False
