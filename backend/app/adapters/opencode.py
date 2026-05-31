"""
OpenCode Adapter - Integration with OpenCode CLI.

OpenCode supports session-based interaction (long-running process).
run_task() internally manages sessions for efficiency.
"""
from typing import AsyncGenerator
import json
import shutil

from app.adapters.base import AgentAdapter, AgentEvent, AgentSession
from app.config import settings
from app.services.process_pool import ProcessPool, ProcessPoolError


class OpenCodeAdapter(AgentAdapter):
    """OpenCode CLI adapter - session-based agent."""

    platform_name = "opencode"

    def __init__(self, pool: ProcessPool | None = None, binary_path: str | None = None):
        self.pool = pool or ProcessPool(settings.CLI_TIMEOUT_SECONDS)
        self.binary_path = binary_path or settings.OPENCODE_BINARY_PATH

    async def run_task(
        self, work_dir: str, instruction: str, context: dict
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Execute a one-shot OpenCode run. Session support remains optional.
        """
        cancel_event = context.get("_cancel_event")
        public_context = {key: value for key, value in context.items() if not key.startswith("_")}
        prompt = f"{instruction}\n\nAgentHub handoff:\n{json.dumps(public_context, ensure_ascii=False)}"
        try:
            result = await self.pool.run(
                [self.binary_path, "run", "--format", "json", "--dir", work_dir, prompt],
                cwd=work_dir,
                cancel_event=cancel_event,
            )
            yield AgentEvent(type="text_delta", content=result.stdout)
        except ProcessPoolError as exc:
            yield AgentEvent(type="error", content=str(exc))
        yield AgentEvent(type="done", content="")

    async def health_check(self) -> bool:
        return shutil.which(self.binary_path) is not None

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
