"""
OpenCode Adapter - Integration with OpenCode CLI.

OpenCode supports session-based interaction (long-running process).
run_task() internally manages sessions for efficiency.
"""
from typing import AsyncGenerator

from app.adapters.base import AgentAdapter, AgentEvent, AgentSession


class OpenCodeAdapter(AgentAdapter):
    """OpenCode CLI adapter - session-based agent."""

    platform_name = "opencode"

    async def run_task(
        self, work_dir: str, instruction: str, context: dict
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Execute task via OpenCode CLI.
        TODO: Implement subprocess management and output parsing
        """
        yield AgentEvent(type="text_delta", content="[OpenCode not implemented]")
        yield AgentEvent(type="done", content="")

    async def health_check(self) -> bool:
        # TODO: check if opencode binary exists
        return False

    async def start_session(self, work_dir: str, system_instruction: str) -> AgentSession:
        """Start an OpenCode session."""
        # TODO: implement
        raise NotImplementedError("OpenCode sessions not yet implemented")

    async def send_message(self, session: AgentSession, message: str) -> AsyncGenerator[AgentEvent, None]:
        """Send message to OpenCode session."""
        # TODO: implement
        yield AgentEvent(type="error", content="Not implemented")

    async def stop_session(self, session: AgentSession) -> None:
        """Stop OpenCode session."""
        # TODO: implement
        pass
