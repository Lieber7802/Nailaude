import json

import httpx
import pytest

from app.services.deepseek_responses_bridge import DeepSeekResponsesBridge, DeepSeekResponsesBridgeError


def sse_data(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


def parse_sse_events(payload: str) -> list[dict]:
    return [
        json.loads(line.removeprefix("data: "))
        for line in payload.splitlines()
        if line.startswith("data: ")
    ]


def test_bridge_converts_codex_responses_input_and_tools_to_deepseek_chat():
    bridge = DeepSeekResponsesBridge(api_key="test-key", model="deepseek-chat")

    payload = bridge.to_chat_payload(
        {
            "model": "deepseek-chat",
            "instructions": "Act as a coding agent.",
            "input": [
                {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": "Create output.txt"}],
                },
                {
                    "type": "function_call",
                    "call_id": "call-1",
                    "name": "shell_command",
                    "arguments": '{"command":"pwd"}',
                },
                {"type": "function_call_output", "call_id": "call-1", "output": "D:/Nailaude"},
            ],
            "tools": [
                {
                    "type": "function",
                    "name": "shell_command",
                    "description": "Run a shell command.",
                    "parameters": {"type": "object", "properties": {"command": {"type": "string"}}},
                }
            ],
            "stream": True,
        }
    )

    assert payload["model"] == "deepseek-chat"
    assert payload["messages"] == [
        {"role": "system", "content": "Act as a coding agent."},
        {"role": "user", "content": "Create output.txt"},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "call-1",
                    "type": "function",
                    "function": {"name": "shell_command", "arguments": '{"command":"pwd"}'},
                }
            ],
        },
        {"role": "tool", "tool_call_id": "call-1", "content": "D:/Nailaude"},
    ]
    assert payload["tools"] == [
        {
            "type": "function",
            "function": {
                "name": "shell_command",
                "description": "Run a shell command.",
                "parameters": {"type": "object", "properties": {"command": {"type": "string"}}},
            },
        }
    ]
    assert payload["stream"] is True


def test_bridge_truncates_large_tool_outputs_before_forwarding_to_deepseek_chat():
    bridge = DeepSeekResponsesBridge(api_key="test-key", model="deepseek-chat")
    long_output = "HEAD\n" + ("x" * 14_000) + "\nTAIL"

    payload = bridge.to_chat_payload(
        {
            "input": [
                {"type": "function_call", "call_id": "call-read", "name": "shell", "arguments": "{}"},
                {"type": "function_call_output", "call_id": "call-read", "output": long_output},
            ]
        }
    )

    tool_message = payload["messages"][-1]

    assert tool_message["role"] == "tool"
    assert tool_message["tool_call_id"] == "call-read"
    assert len(tool_message["content"]) < 7_000
    assert "HEAD" in tool_message["content"]
    assert "TAIL" in tool_message["content"]
    assert "Nailaude truncated" in tool_message["content"]


def test_bridge_groups_consecutive_function_calls_before_tool_outputs():
    bridge = DeepSeekResponsesBridge(api_key="test-key", model="deepseek-chat")

    payload = bridge.to_chat_payload(
        {
            "input": [
                {"type": "function_call", "call_id": "call-1", "name": "shell", "arguments": '{"command":"pwd"}'},
                {"type": "function_call", "call_id": "call-2", "name": "shell", "arguments": '{"command":"ls"}'},
                {"type": "function_call_output", "call_id": "call-1", "output": "/tmp/project"},
                {"type": "function_call_output", "call_id": "call-2", "output": "index.html"},
            ]
        }
    )

    assert [message["role"] for message in payload["messages"]] == ["assistant", "tool", "tool"]
    assert [call["id"] for call in payload["messages"][0]["tool_calls"]] == ["call-1", "call-2"]
    assert payload["messages"][1]["tool_call_id"] == "call-1"
    assert payload["messages"][2]["tool_call_id"] == "call-2"


@pytest.mark.asyncio
async def test_bridge_translates_deepseek_text_stream_to_responses_events():
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url == httpx.URL("https://api.deepseek.com/chat/completions")
        return httpx.Response(
            200,
            text="".join(
                [
                    sse_data({"choices": [{"delta": {"content": "OK"}}]}),
                    sse_data({"choices": [{"delta": {}, "finish_reason": "stop"}]}),
                    "data: [DONE]\n\n",
                ]
            ),
        )

    bridge = DeepSeekResponsesBridge(
        api_key="test-key",
        model="deepseek-chat",
        transport=httpx.MockTransport(handler),
    )

    response = await bridge.handle_responses_request({"input": [], "stream": True})
    events = parse_sse_events(response)

    assert [event["type"] for event in events] == [
        "response.created",
        "response.output_item.added",
        "response.content_part.added",
        "response.output_text.delta",
        "response.output_text.done",
        "response.content_part.done",
        "response.output_item.done",
        "response.completed",
    ]
    assert events[3]["delta"] == "OK"
    assert events[-1]["response"]["status"] == "completed"


@pytest.mark.asyncio
async def test_bridge_includes_deepseek_error_body_in_normalized_failures():
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": {"message": "Input tokens are too long"}})

    bridge = DeepSeekResponsesBridge(api_key="test-key", transport=httpx.MockTransport(handler))

    with pytest.raises(DeepSeekResponsesBridgeError, match="Input tokens are too long"):
        await bridge.handle_responses_request({"input": [], "stream": True})


@pytest.mark.asyncio
async def test_bridge_translates_deepseek_function_call_stream_to_responses_events():
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text="".join(
                [
                    sse_data(
                        {
                            "choices": [
                                {
                                    "delta": {
                                        "tool_calls": [
                                            {
                                                "index": 0,
                                                "id": "call-1",
                                                "function": {"name": "shell_command", "arguments": '{"command":'},
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    ),
                    sse_data(
                        {
                            "choices": [
                                {
                                    "delta": {
                                        "tool_calls": [{"index": 0, "function": {"arguments": '"pwd"}'}}]
                                    },
                                    "finish_reason": "tool_calls",
                                }
                            ]
                        }
                    ),
                    "data: [DONE]\n\n",
                ]
            ),
        )

    bridge = DeepSeekResponsesBridge(api_key="test-key", transport=httpx.MockTransport(handler))

    response = await bridge.handle_responses_request({"input": [], "stream": True})
    events = parse_sse_events(response)

    assert [event["type"] for event in events] == [
        "response.created",
        "response.output_item.added",
        "response.function_call_arguments.delta",
        "response.function_call_arguments.delta",
        "response.function_call_arguments.done",
        "response.output_item.done",
        "response.completed",
    ]
    assert events[4]["arguments"] == '{"command":"pwd"}'


@pytest.mark.asyncio
async def test_bridge_round_trips_deepseek_reasoning_content_for_tool_calls():
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            text="".join(
                [
                    sse_data({"choices": [{"delta": {"reasoning_content": "Need to inspect files. "}}]}),
                    sse_data(
                        {
                            "choices": [
                                {
                                    "delta": {
                                        "tool_calls": [
                                            {
                                                "index": 0,
                                                "id": "call-1",
                                                "function": {"name": "shell_command", "arguments": '{"command":"ls"}'},
                                            }
                                        ]
                                    }
                                }
                            ]
                        }
                    ),
                    "data: [DONE]\n\n",
                ]
            ),
        )

    bridge = DeepSeekResponsesBridge(api_key="test-key", transport=httpx.MockTransport(handler))

    await bridge.handle_responses_request({"input": [], "stream": True})
    payload = bridge.to_chat_payload(
        {
            "input": [
                {
                    "type": "function_call",
                    "call_id": "call-1",
                    "name": "shell_command",
                    "arguments": '{"command":"ls"}',
                },
                {"type": "function_call_output", "call_id": "call-1", "output": "index.html"},
            ]
        }
    )

    assert payload["messages"][0]["role"] == "assistant"
    assert payload["messages"][0]["reasoning_content"] == "Need to inspect files. "
