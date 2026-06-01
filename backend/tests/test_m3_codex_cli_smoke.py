import json
from pathlib import Path

import httpx
import pytest

from app.adapters.codex import CodexAdapter, resolve_codex_binary
from app.services.deepseek_responses_bridge import DeepSeekResponsesBridge
from app.services.process_pool import ProcessPool


@pytest.mark.asyncio
async def test_real_codex_cli_runs_through_isolated_fake_deepseek_bridge(tmp_path):
    binary_path = resolve_codex_binary("codex")
    if not Path(binary_path).is_file():
        pytest.skip("runnable Codex CLI cache is not installed")
    upstream_payloads: list[dict] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        upstream_payloads.append(json.loads(request.content))
        return httpx.Response(
            200,
            text='data: {"choices":[{"delta":{"content":"OK"}}]}\n\n'
            'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}\n\n'
            "data: [DONE]\n\n",
        )

    def bridge_factory():
        return DeepSeekResponsesBridge(
            api_key="fake-deepseek-key",
            model="deepseek-chat",
            transport=httpx.MockTransport(handler),
        )

    adapter = CodexAdapter(
        pool=ProcessPool(default_timeout=25),
        binary_path=binary_path,
        bridge_factory=bridge_factory,
    )

    events = [event async for event in adapter.run_task(str(tmp_path), "Reply with OK only. Do not use tools.", {})]

    assert [(event.type, event.content) for event in events] == [("text_delta", "OK"), ("done", "")]
    assert len(upstream_payloads) == 1
    assert upstream_payloads[0]["model"] == "deepseek-chat"
