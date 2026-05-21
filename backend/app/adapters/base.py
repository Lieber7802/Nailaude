"""
AgentAdapter - Abstract base class for all agent platform adapters.

Core interface: run_task() - executes a task and yields events.
Optional: session-based interface for long-running agent conversations.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncGenerator


@dataclass
class AgentEvent:
    """Event emitted by an adapter during task execution."""
    type: str  # text_delta | artifact | file_created | file_modified | team_note | thinking | done | error
    content: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class AgentSession:
    """Represents an active session with a session-based agent."""
    session_id: str
    platform_id: str
    work_dir: str


class AgentAdapter(ABC):
    """Abstract base class for Agent platform adapters."""

    platform_name: str = "base"

    @abstractmethod
    async def run_task(
        self, work_dir: str, instruction: str, context: dict
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Core interface: Execute a task and stream back events.

        Args:
            work_dir: Project directory path
            instruction: Task instruction from user/orchestrator
            context: Layered context (history, project state, etc.)

        Yields:
            AgentEvent instances as the task progresses
        """
        yield AgentEvent(type="done")  # type: ignore

    async def health_check(self) -> bool:
        """Check if this adapter's platform is available."""
        return True

    # Optional: session-based interface (for long-running agents)
    async def start_session(self, work_dir: str, system_instruction: str) -> AgentSession:
        """Start a persistent session (optional, override if supported)."""
        raise NotImplementedError(f"{self.platform_name} does not support sessions")

    async def send_message(self, session: AgentSession, message: str) -> AsyncGenerator[AgentEvent, None]:
        """Send message to existing session (optional)."""
        raise NotImplementedError(f"{self.platform_name} does not support sessions")
        yield  # type: ignore

    async def stop_session(self, session: AgentSession) -> None:
        """Stop a session (optional)."""
        raise NotImplementedError(f"{self.platform_name} does not support sessions")
