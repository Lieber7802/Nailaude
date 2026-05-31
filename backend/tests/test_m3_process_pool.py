import asyncio
import sys
from time import perf_counter

import pytest

from app.services.process_pool import ProcessPool, ProcessPoolError


@pytest.mark.asyncio
async def test_process_pool_captures_successful_output(tmp_path):
    pool = ProcessPool(default_timeout=2)

    result = await pool.run([sys.executable, "-c", "print('hello')"], cwd=str(tmp_path))

    assert result.returncode == 0
    assert result.stdout.strip() == "hello"


@pytest.mark.asyncio
async def test_process_pool_raises_on_non_zero_exit(tmp_path):
    pool = ProcessPool(default_timeout=2)

    with pytest.raises(ProcessPoolError, match="exit code 3"):
        await pool.run([sys.executable, "-c", "raise SystemExit(3)"], cwd=str(tmp_path))


@pytest.mark.asyncio
async def test_process_pool_terminates_timed_out_process(tmp_path):
    pool = ProcessPool(default_timeout=0.05)

    with pytest.raises(ProcessPoolError, match="timed out"):
        await pool.run([sys.executable, "-c", "import time; time.sleep(1)"], cwd=str(tmp_path))

    assert pool.active_count == 0


@pytest.mark.asyncio
async def test_process_pool_honors_cancel_event(tmp_path):
    pool = ProcessPool(default_timeout=2)
    cancel_event = asyncio.Event()
    task = asyncio.create_task(
        pool.run([sys.executable, "-c", "import time; time.sleep(1)"], cwd=str(tmp_path), cancel_event=cancel_event)
    )
    await asyncio.sleep(0.05)
    cancel_event.set()

    with pytest.raises(ProcessPoolError, match="cancelled"):
        await task

    assert pool.active_count == 0


@pytest.mark.asyncio
async def test_process_pool_limits_cli_concurrency_across_pool_instances(tmp_path):
    first = ProcessPool(default_timeout=2, max_concurrency=1)
    second = ProcessPool(default_timeout=2, max_concurrency=1)
    started = perf_counter()

    await asyncio.gather(
        first.run([sys.executable, "-c", "import time; time.sleep(0.15)"], cwd=str(tmp_path)),
        second.run([sys.executable, "-c", "import time; time.sleep(0.15)"], cwd=str(tmp_path)),
    )

    assert perf_counter() - started >= 0.25
    assert first.active_count == second.active_count == 0
