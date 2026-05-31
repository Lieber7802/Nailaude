"""Bounded asyncio subprocess lifecycle management for CLI adapters."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from weakref import WeakKeyDictionary

from app.config import settings


class ProcessPoolError(RuntimeError):
    """Normalized CLI process failure."""


@dataclass
class ProcessResult:
    stdout: str
    stderr: str
    returncode: int


class ProcessPool:
    _semaphores: WeakKeyDictionary = WeakKeyDictionary()

    def __init__(
        self,
        default_timeout: float = 120,
        log_limit: int = 20_000,
        max_concurrency: int | None = None,
    ):
        self.default_timeout = default_timeout
        self.log_limit = log_limit
        self.max_concurrency = max_concurrency or settings.CLI_MAX_CONCURRENCY
        self._active: set[asyncio.subprocess.Process] = set()

    @property
    def active_count(self) -> int:
        return len(self._active)

    async def run(
        self,
        command: list[str],
        cwd: str,
        timeout: float | None = None,
        cancel_event: asyncio.Event | None = None,
    ) -> ProcessResult:
        async with self._semaphore():
            return await self._run(command, cwd, timeout=timeout, cancel_event=cancel_event)

    async def _run(
        self,
        command: list[str],
        cwd: str,
        timeout: float | None = None,
        cancel_event: asyncio.Event | None = None,
    ) -> ProcessResult:
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except OSError as exc:
            raise ProcessPoolError(f"failed to start process: {exc}") from exc

        self._active.add(process)
        communicate = asyncio.create_task(process.communicate())
        cancel_wait = asyncio.create_task(cancel_event.wait()) if cancel_event else None
        try:
            wait_for = {communicate}
            if cancel_wait:
                wait_for.add(cancel_wait)
            done, _ = await asyncio.wait(wait_for, timeout=timeout or self.default_timeout, return_when=asyncio.FIRST_COMPLETED)
            if communicate not in done:
                await self._terminate(process)
                if cancel_wait and cancel_wait in done:
                    raise ProcessPoolError("process cancelled")
                raise ProcessPoolError("process timed out")
            stdout_bytes, stderr_bytes = communicate.result()
            result = ProcessResult(
                stdout=self._decode(stdout_bytes),
                stderr=self._decode(stderr_bytes),
                returncode=int(process.returncode or 0),
            )
            if result.returncode != 0:
                raise ProcessPoolError(f"process exited with exit code {result.returncode}: {result.stderr}")
            return result
        except asyncio.CancelledError:
            await self._terminate(process)
            raise
        finally:
            if cancel_wait:
                cancel_wait.cancel()
            if not communicate.done():
                communicate.cancel()
            self._active.discard(process)

    async def _terminate(self, process: asyncio.subprocess.Process) -> None:
        if process.returncode is None:
            process.kill()
            await process.wait()

    def _decode(self, value: bytes) -> str:
        return value.decode("utf-8", errors="replace")[-self.log_limit :]

    def _semaphore(self) -> asyncio.Semaphore:
        loop = asyncio.get_running_loop()
        by_limit = self._semaphores.setdefault(loop, {})
        if self.max_concurrency not in by_limit:
            by_limit[self.max_concurrency] = asyncio.Semaphore(self.max_concurrency)
        return by_limit[self.max_concurrency]
