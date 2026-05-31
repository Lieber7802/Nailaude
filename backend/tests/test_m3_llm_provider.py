import httpx
import pytest

from app.adapters.llm_provider import LLMProviderAdapter
from app.services.llm_client import LLMClient


@pytest.mark.asyncio
async def test_llm_provider_streams_client_deltas_and_done():
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text='data: {"choices":[{"delta":{"content":"hello"}}]}\ndata: [DONE]',
        )

    adapter = LLMProviderAdapter(LLMClient(api_key="test-key", transport=httpx.MockTransport(handler)))
    events = [event async for event in adapter.run_task(".", "say hello", {})]

    assert [event.type for event in events] == ["text_delta", "done"]
    assert events[0].content == "hello"


@pytest.mark.asyncio
async def test_llm_provider_emits_error_when_key_is_missing():
    adapter = LLMProviderAdapter(LLMClient(api_key=""))
    events = [event async for event in adapter.run_task(".", "say hello", {})]

    assert [event.type for event in events] == ["error", "done"]
    assert "DEEPSEEK_API_KEY" in events[0].content
