"""Bounded asyncio subprocess lifecycle management for CLI adapters."""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass
from weakref import WeakKeyDictionary

from app.config import settings


PIPE_DRAIN_TIMEOUT_SECONDS = 0.5


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
        env: dict[str, str] | None = None,
    ) -> ProcessResult:
        async with self._semaphore():
            return await self._run(command, cwd, timeout=timeout, cancel_event=cancel_event, env=env)

    async def _run(
        self,
        command: list[str],
        cwd: str,
        timeout: float | None = None,
        cancel_event: asyncio.Event | None = None,
        env: dict[str, str] | None = None,
    ) -> ProcessResult:
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env or os.environ.copy(),
            )
        except OSError as exc:
            raise ProcessPoolError(f"failed to start process: {exc}") from exc

        self._active.add(process)
        stdout = bytearray()
        stderr = bytearray()
        stdout_read = asyncio.create_task(self._capture_stream(process.stdout, stdout))
        stderr_read = asyncio.create_task(self._capture_stream(process.stderr, stderr))
        process_wait = asyncio.create_task(self._wait_for_exit(process))
        cancel_wait = asyncio.create_task(cancel_event.wait()) if cancel_event else None
        try:
            wait_for = {process_wait}
            if cancel_wait:
                wait_for.add(cancel_wait)
            done, _ = await asyncio.wait(wait_for, timeout=timeout or self.default_timeout, return_when=asyncio.FIRST_COMPLETED)
            if process_wait not in done:
                await self._terminate(process)
                await self._stop_capture(process, stdout_read, stderr_read)
                if cancel_wait and cancel_wait in done:
                    raise ProcessPoolError("process cancelled")
                raise ProcessPoolError("process timed out")
            await self._drain_capture(process, stdout_read, stderr_read)
            result = ProcessResult(
                stdout=self._decode(bytes(stdout)),
                stderr=self._decode(bytes(stderr)),
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
            if not process_wait.done():
                process_wait.cancel()
            self._active.discard(process)

    async def _terminate(self, process: asyncio.subprocess.Process) -> None:
        if process.returncode is None:
            process.kill()
            await asyncio.wait_for(self._wait_for_exit(process), timeout=1)

    def _decode(self, value: bytes) -> str:
        return value.decode("utf-8", errors="replace")[-self.log_limit :]

    async def _capture_stream(self, stream: asyncio.StreamReader | None, buffer: bytearray) -> None:
        if stream is None:
            return
        while chunk := await stream.read(4096):
            buffer.extend(chunk)

    async def _wait_for_exit(self, process: asyncio.subprocess.Process) -> int:
        while process.returncode is None:
            await asyncio.sleep(0.02)
        return int(process.returncode)

    async def _drain_capture(self, process: asyncio.subprocess.Process, *tasks: asyncio.Task) -> None:
        try:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=PIPE_DRAIN_TIMEOUT_SECONDS)
        except asyncio.TimeoutError:
            await self._stop_capture(process, *tasks)

    async def _stop_capture(self, process: asyncio.subprocess.Process, *tasks: asyncio.Task) -> None:
        for task in tasks:
            task.cancel()
        for stream in (process.stdout, process.stderr):
            transport = getattr(stream, "_transport", None)
            if transport:
                transport.close()
        await asyncio.gather(*tasks, return_exceptions=True)

    def _semaphore(self) -> asyncio.Semaphore:
        loop = asyncio.get_running_loop()
        by_limit = self._semaphores.setdefault(loop, {})
        if self.max_concurrency not in by_limit:
            by_limit[self.max_concurrency] = asyncio.Semaphore(self.max_concurrency)
        return by_limit[self.max_concurrency]
