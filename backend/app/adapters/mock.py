"""
MockAdapter - Permanent mock adapter for development, testing, and demo fallback.

This adapter simulates agent behavior without any external dependencies.
It is NOT a temporary component - it stays in production as a fallback.
"""
from typing import AsyncGenerator

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
        Simulate a task execution with streaming text output.
        TODO: Implement full mock scenarios (code gen, diff, team notes)
        """
        yield AgentEvent(type="text_delta", content="Mock response for: ")
        yield AgentEvent(type="text_delta", content=instruction[:50])
        yield AgentEvent(type="done", content="")

    async def health_check(self) -> bool:
        return True
