"""Loopback-only adapter from Codex Responses requests to DeepSeek chat completions."""
from __future__ import annotations

import asyncio
import json
import secrets
from time import time
from uuid import uuid4

import httpx

from app.config import settings


MAX_TOOL_OUTPUT_CHARS = 6_000
MAX_DEEPSEEK_ERROR_BODY_CHARS = 2_000


class DeepSeekResponsesBridgeError(RuntimeError):
    """Normalized protocol bridge failure."""


class DeepSeekResponsesBridge:
    """Serve the Responses API shape expected by Codex over a loopback socket."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        token: str | None = None,
    ):
        self.api_key = settings.DEEPSEEK_API_KEY if api_key is None else api_key
        self.deepseek_base_url = (base_url or settings.DEEPSEEK_BASE_URL).rstrip("/")
        self.model = model or settings.DEEPSEEK_MODEL
        self.transport = transport
        self.token = token or secrets.token_urlsafe(32)
        self._server: asyncio.Server | None = None
        self._port: int | None = None
        self._reasoning_by_call_id: dict[str, str] = {}

    @property
    def base_url(self) -> str:
        if self._port is None:
            raise DeepSeekResponsesBridgeError("bridge is not running")
        return f"http://127.0.0.1:{self._port}"

    async def __aenter__(self):
        if not self.api_key:
            raise DeepSeekResponsesBridgeError("DEEPSEEK_API_KEY is not configured")
        self._server = await asyncio.start_server(self._handle_connection, "127.0.0.1", 0)
        sockets = self._server.sockets or []
        if not sockets:
            raise DeepSeekResponsesBridgeError("bridge failed to bind a loopback socket")
        self._port = int(sockets[0].getsockname()[1])
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        if self._server:
            self._server.close()
            await self._server.wait_closed()
        self._server = None
        self._port = None

    def to_chat_payload(self, payload: dict) -> dict:
        messages: list[dict] = []
        pending_tool_calls: list[dict] = []
        pending_reasoning: list[str] = []

        def flush_function_calls() -> None:
            if not pending_tool_calls:
                return
            message = {"role": "assistant", "content": None, "tool_calls": list(pending_tool_calls)}
            reasoning = "\n".join(item for item in pending_reasoning if item)
            if reasoning:
                message["reasoning_content"] = reasoning
            messages.append(message)
            pending_tool_calls.clear()
            pending_reasoning.clear()

        instructions = payload.get("instructions")
        if instructions:
            messages.append({"role": "system", "content": str(instructions)})
        for item in payload.get("input") or []:
            if not isinstance(item, dict):
                continue
            item_type = item.get("type")
            if item_type == "message":
                flush_function_calls()
                messages.append(
                    {
                        "role": self._chat_role(str(item.get("role") or "user")),
                        "content": self._content_text(item.get("content")),
                    }
                )
            elif item_type == "function_call":
                call_id = str(item.get("call_id") or item.get("id") or "")
                pending_tool_calls.append(
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {
                            "name": str(item.get("name") or ""),
                            "arguments": str(item.get("arguments") or ""),
                        },
                    }
                )
                if reasoning := self._reasoning_by_call_id.get(call_id):
                    pending_reasoning.append(reasoning)
            elif item_type == "function_call_output":
                flush_function_calls()
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": str(item.get("call_id") or ""),
                        "content": self._tool_output_text(item.get("output")),
                    }
                )
        flush_function_calls()
        result = {"model": self.model, "messages": messages, "stream": True}
        tools = [self._chat_tool(tool) for tool in payload.get("tools") or [] if tool.get("type") == "function"]
        if tools:
            result["tools"] = tools
        tool_choice = payload.get("tool_choice")
        if tool_choice in {"auto", "none", "required"}:
            result["tool_choice"] = tool_choice
        return result

    async def handle_responses_request(self, payload: dict) -> str:
        response_id = f"resp_{uuid4().hex}"
        output_items: list[dict] = []
        events: list[dict] = []
        sequence = 0

        def emit(event_type: str, **values):
            nonlocal sequence
            sequence += 1
            events.append({"type": event_type, "sequence_number": sequence, **values})

        emit("response.created", response=self._response(response_id, "in_progress", []))
        message_item: dict | None = None
        message_text = ""
        reasoning_text = ""
        tool_items: dict[int, dict] = {}

        async with httpx.AsyncClient(transport=self.transport, timeout=settings.DEEPSEEK_TIMEOUT_SECONDS) as client:
            async with client.stream(
                "POST",
                f"{self.deepseek_base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=self.to_chat_payload(payload),
            ) as response:
                if response.status_code >= 400:
                    body = (await response.aread()).decode("utf-8", errors="replace")
                    if len(body) > MAX_DEEPSEEK_ERROR_BODY_CHARS:
                        body = f"{body[:MAX_DEEPSEEK_ERROR_BODY_CHARS]}..."
                    raise DeepSeekResponsesBridgeError(
                        f"DeepSeek request failed {response.status_code}: {body}"
                    )
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    raw = line.removeprefix("data:").strip()
                    if not raw or raw == "[DONE]":
                        continue
                    chunk = json.loads(raw)
                    choices = chunk.get("choices") or []
                    if not choices:
                        continue
                    delta = choices[0].get("delta") or {}
                    reasoning = delta.get("reasoning_content")
                    if reasoning:
                        reasoning_text += str(reasoning)
                    content = delta.get("content")
                    if content:
                        if message_item is None:
                            message_item = self._message_item()
                            emit("response.output_item.added", output_index=len(output_items), item=message_item)
                            emit(
                                "response.content_part.added",
                                item_id=message_item["id"],
                                output_index=len(output_items),
                                content_index=0,
                                part={"type": "output_text", "text": "", "annotations": []},
                            )
                        message_text += str(content)
                        emit(
                            "response.output_text.delta",
                            item_id=message_item["id"],
                            output_index=len(output_items),
                            content_index=0,
                            delta=str(content),
                        )
                    for tool_call in delta.get("tool_calls") or []:
                        index = int(tool_call.get("index") or 0)
                        item = tool_items.get(index)
                        function = tool_call.get("function") or {}
                        if item is None:
                            item = self._function_item(
                                str(tool_call.get("id") or f"call_{uuid4().hex}"),
                                str(function.get("name") or ""),
                            )
                            tool_items[index] = item
                            emit("response.output_item.added", output_index=len(output_items) + index, item=item)
                        arguments = str(function.get("arguments") or "")
                        if arguments:
                            item["arguments"] += arguments
                            emit(
                                "response.function_call_arguments.delta",
                                item_id=item["id"],
                                output_index=len(output_items) + index,
                                delta=arguments,
                            )

        if message_item is not None:
            complete_message = {
                **message_item,
                "status": "completed",
                "content": [{"type": "output_text", "text": message_text, "annotations": []}],
            }
            emit(
                "response.output_text.done",
                item_id=message_item["id"],
                output_index=len(output_items),
                content_index=0,
                text=message_text,
            )
            emit(
                "response.content_part.done",
                item_id=message_item["id"],
                output_index=len(output_items),
                content_index=0,
                part=complete_message["content"][0],
            )
            emit("response.output_item.done", output_index=len(output_items), item=complete_message)
            output_items.append(complete_message)
        for index in sorted(tool_items):
            item = {**tool_items[index], "status": "completed"}
            if reasoning_text:
                self._reasoning_by_call_id[item["call_id"]] = reasoning_text
            output_index = len(output_items)
            emit(
                "response.function_call_arguments.done",
                item_id=item["id"],
                output_index=output_index,
                arguments=item["arguments"],
            )
            emit("response.output_item.done", output_index=output_index, item=item)
            output_items.append(item)
        emit("response.completed", response=self._response(response_id, "completed", output_items))
        return "".join(f"event: {event['type']}\ndata: {json.dumps(event)}\n\n" for event in events)

    async def _handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            header_bytes = await reader.readuntil(b"\r\n\r\n")
            header_text = header_bytes.decode("latin-1")
            request_line, *header_lines = header_text.split("\r\n")
            method, path, _ = request_line.split(" ", 2)
            headers = {
                name.strip().lower(): value.strip()
                for line in header_lines
                if ":" in line
                for name, value in [line.split(":", 1)]
            }
            content_length = int(headers.get("content-length") or 0)
            body = await reader.readexactly(content_length) if content_length else b"{}"
            if method != "POST" or path.rstrip("/") != "/responses":
                await self._write_json(writer, 404, {"error": {"message": "not found"}})
                return
            if headers.get("authorization") != f"Bearer {self.token}":
                await self._write_json(writer, 401, {"error": {"message": "unauthorized"}})
                return
            payload = json.loads(body)
            response = await self.handle_responses_request(payload)
            await self._write_response(writer, 200, "text/event-stream", response.encode())
        except (DeepSeekResponsesBridgeError, httpx.HTTPError, json.JSONDecodeError, asyncio.IncompleteReadError) as exc:
            await self._write_json(writer, 502, {"error": {"message": str(exc)}})
        finally:
            writer.close()
            await writer.wait_closed()

    async def _write_json(self, writer: asyncio.StreamWriter, status: int, payload: dict) -> None:
        await self._write_response(writer, status, "application/json", json.dumps(payload).encode())

    async def _write_response(
        self, writer: asyncio.StreamWriter, status: int, content_type: str, body: bytes
    ) -> None:
        reason = {200: "OK", 401: "Unauthorized", 404: "Not Found", 502: "Bad Gateway"}.get(status, "Error")
        writer.write(
            (
                f"HTTP/1.1 {status} {reason}\r\n"
                f"Content-Type: {content_type}\r\n"
                f"Content-Length: {len(body)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode()
            + body
        )
        await writer.drain()

    def _response(self, response_id: str, status: str, output: list[dict]) -> dict:
        return {
            "id": response_id,
            "object": "response",
            "created_at": int(time()),
            "status": status,
            "model": self.model,
            "output": output,
        }

    def _message_item(self) -> dict:
        return {"id": f"msg_{uuid4().hex}", "type": "message", "status": "in_progress", "role": "assistant", "content": []}

    def _function_item(self, call_id: str, name: str) -> dict:
        return {
            "id": f"fc_{uuid4().hex}",
            "type": "function_call",
            "status": "in_progress",
            "call_id": call_id,
            "name": name,
            "arguments": "",
        }

    def _chat_tool(self, tool: dict) -> dict:
        return {
            "type": "function",
            "function": {
                "name": str(tool.get("name") or ""),
                "description": str(tool.get("description") or ""),
                "parameters": tool.get("parameters") or {},
            },
        }

    def _chat_role(self, role: str) -> str:
        return "system" if role == "developer" else role

    def _content_text(self, content) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(
                str(part.get("text") or part.get("content") or "")
                for part in content
                if isinstance(part, dict)
            )
        if content is None:
            return ""
        return json.dumps(content, ensure_ascii=False, default=str)

    def _tool_output_text(self, output) -> str:
        return self._truncate_text(self._content_text(output), MAX_TOOL_OUTPUT_CHARS, "tool output")

    def _truncate_text(self, text: str, limit: int, label: str) -> str:
        if len(text) <= limit:
            return text

        marker = ""
        for _ in range(3):
            available = max(0, limit - len(marker))
            head_chars = available // 2
            tail_chars = available - head_chars
            omitted = max(0, len(text) - head_chars - tail_chars)
            marker = (
                f"\n\n[Nailaude truncated {omitted} chars from {label} "
                "to keep the DeepSeek bridge request valid.]\n\n"
            )

        available = max(0, limit - len(marker))
        if available <= 0:
            return marker[:limit]
        head_chars = available // 2
        tail_chars = available - head_chars
        return text[:head_chars] + marker + text[-tail_chars:]
