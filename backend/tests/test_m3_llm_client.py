import asyncio
import json

import httpx
import pytest

from app.services.llm_client import LLMClient, LLMClientError


def response(payload: dict, status_code: int = 200) -> httpx.Response:
    return httpx.Response(status_code, json=payload)


@pytest.mark.asyncio
async def test_llm_client_requests_json_and_records_usage():
    async def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert request.url == httpx.URL("https://api.deepseek.com/chat/completions")
        assert body["model"] == "deepseek-v4-flash"
        assert body["response_format"] == {"type": "json_object"}
        return response(
            {
                "choices": [{"message": {"content": '{"status":"ready"}'}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 3, "total_tokens": 15},
            }
        )

    client = LLMClient(api_key="test-key", transport=httpx.MockTransport(handler))
    result = await client.request_json([{"role": "user", "content": "plan"}])

    assert result.content == {"status": "ready"}
    assert result.usage.total_tokens == 15
    assert client.last_usage == result.usage


@pytest.mark.asyncio
async def test_llm_client_streams_text_deltas_and_records_usage():
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text="\n".join(
                [
                    'data: {"choices":[{"delta":{"content":"hello "}}]}',
                    'data: {"choices":[{"delta":{"content":"world"}}],"usage":{"total_tokens":9}}',
                    "data: [DONE]",
                ]
            ),
        )

    client = LLMClient(api_key="test-key", transport=httpx.MockTransport(handler))
    chunks = [chunk async for chunk in client.stream_text([{"role": "user", "content": "write"}])]

    assert chunks == ["hello ", "world"]
    assert client.last_usage.total_tokens == 9


@pytest.mark.asyncio
async def test_llm_client_yields_sse_chunks_before_response_completes():
    release_second_chunk = asyncio.Event()

    class DelayedSSEStream(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'data: {"choices":[{"delta":{"content":"first"}}]}\n\n'
            await release_second_chunk.wait()
            yield b'data: {"choices":[{"delta":{"content":"second"}}]}\n\ndata: [DONE]\n\n'

    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, stream=DelayedSSEStream())

    client = LLMClient(api_key="test-key", transport=httpx.MockTransport(handler))
    stream = client.stream_text([{"role": "user", "content": "write"}])

    assert await anext(stream) == "first"
    release_second_chunk.set()
    assert await anext(stream) == "second"
    with pytest.raises(StopAsyncIteration):
        await anext(stream)


@pytest.mark.asyncio
async def test_llm_client_retries_one_transient_failure():
    attempts = 0

    async def handler(_: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise httpx.ConnectError("offline")
        return response({"choices": [{"message": {"content": "{}"}}], "usage": {"total_tokens": 1}})

    client = LLMClient(api_key="test-key", transport=httpx.MockTransport(handler), retry_delay=0)
    await client.request_json([{"role": "user", "content": "retry"}])

    assert attempts == 2


@pytest.mark.asyncio
async def test_llm_client_requires_api_key():
    client = LLMClient(api_key="")

    with pytest.raises(LLMClientError, match="DEEPSEEK_API_KEY"):
        await client.request_json([{"role": "user", "content": "plan"}])
