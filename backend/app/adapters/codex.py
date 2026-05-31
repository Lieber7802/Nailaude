"""
Codex Adapter - Integration with OpenAI Codex CLI.

Codex uses a one-shot task model (one process per task).
run_task() spawns a new process each time.
"""
from typing import AsyncGenerator
import json
import shutil

from app.adapters.base import AgentAdapter, AgentEvent
from app.config import settings
from app.services.process_pool import ProcessPool, ProcessPoolError


class CodexAdapter(AgentAdapter):
    """Codex CLI adapter - one-shot task execution."""

    platform_name = "codex"

    def __init__(self, pool: ProcessPool | None = None, binary_path: str | None = None):
        self.pool = pool or ProcessPool(settings.CLI_TIMEOUT_SECONDS)
        self.binary_path = binary_path or settings.CODEX_BINARY_PATH

    async def run_task(
        self, work_dir: str, instruction: str, context: dict
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Execute a Codex one-shot task when a usable CLI is installed.
        """
        cancel_event = context.get("_cancel_event")
        public_context = {key: value for key, value in context.items() if not key.startswith("_")}
        prompt = f"{instruction}\n\nAgentHub handoff:\n{json.dumps(public_context, ensure_ascii=False)}"
        try:
            result = await self.pool.run(
                [self.binary_path, "exec", "--full-auto", prompt],
                cwd=work_dir,
                cancel_event=cancel_event,
            )
            yield AgentEvent(type="text_delta", content=result.stdout)
        except ProcessPoolError as exc:
            yield AgentEvent(type="error", content=str(exc))
        yield AgentEvent(type="done", content="")

    async def health_check(self) -> bool:
        if shutil.which(self.binary_path) is None:
            return False
        try:
            await self.pool.run([self.binary_path, "--help"], cwd=".", timeout=5)
        except ProcessPoolError:
            return False
        return True
