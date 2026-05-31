import json

import httpx
import pytest

from app.adapters.llm_provider import LLMProviderAdapter
from app.services.agent_manager import AgentManagerService


def _sse_chunk(payload: dict) -> bytes:
    return f"data: {json.dumps(payload)}\n\n".encode()


@pytest.mark.asyncio
async def test_llm_provider_streams_deepseek_text_deltas():
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == httpx.URL("https://api.deepseek.com/chat/completions")
        assert request.headers["authorization"] == "Bearer test-key"
        body = json.loads(request.content)
        assert body["model"] == "deepseek-v4-flash"
        assert body["stream"] is True
        assert body["messages"][0]["role"] == "system"
        assert body["messages"][-1] == {"role": "user", "content": "build a page"}
        chunks = [
            _sse_chunk({"choices": [{"delta": {"content": "Hello"}}]}),
            _sse_chunk({"choices": [{"delta": {"content": " world"}}]}),
            b"data: [DONE]\n\n",
        ]
        return httpx.Response(200, content=b"".join(chunks))

    adapter = LLMProviderAdapter(api_key="test-key", client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))

    events = [event async for event in adapter.run_task("workspaces/demo", "build a page", {"systemInstruction": "Be terse"})]

    assert [(event.type, event.content) for event in events] == [
        ("text_delta", "Hello"),
        ("text_delta", " world"),
        ("done", ""),
    ]


@pytest.mark.asyncio
async def test_llm_provider_reports_missing_api_key_without_network_call():
    adapter = LLMProviderAdapter(api_key="", client=httpx.AsyncClient(transport=httpx.MockTransport(lambda request: None)))

    events = [event async for event in adapter.run_task("workspaces/demo", "hello", {})]

    assert events[0].type == "error"
    assert "DEEPSEEK_API_KEY" in events[0].content
    assert events[-1].type == "done"


@pytest.mark.asyncio
async def test_agent_manager_returns_cached_llm_adapter(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    manager = AgentManagerService()

    adapter = await manager.get_adapter("llm")
    same_adapter = await manager.get_adapter("llm")

    assert adapter is same_adapter
    assert adapter.platform_name == "llm"


def test_put_agent_update_matches_api_spec(client):
    agents = client.get("/api/v1/agents").json()["data"]
    response = client.post(
        "/api/v1/agents",
        json={
            "name": "产品经理",
            "avatar": "P",
            "description": "整理需求",
            "capabilities": ["产品"],
            "systemInstruction": "输出结构化 PRD",
            "platformId": "llm",
        },
    )
    assert response.status_code == 200
    agent = response.json()["data"]

    updated = client.put(f"/api/v1/agents/{agent['id']}", json={"description": "整理需求和验收标准"})

    assert updated.status_code == 200
    assert updated.json()["data"]["description"] == "整理需求和验收标准"
    assert len(agents) >= 3
