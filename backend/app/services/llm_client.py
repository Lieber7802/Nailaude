"""Small OpenAI-compatible client shared by DeepSeek-backed services."""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from time import perf_counter
from typing import AsyncGenerator

import httpx

from app.config import settings


class LLMClientError(RuntimeError):
    """Normalized failure raised by the reusable LLM client."""


@dataclass
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    elapsed_ms: int = 0
    model: str = ""


@dataclass
class LLMJSONResult:
    content: dict
    usage: LLMUsage


class LLMClient:
    """DeepSeek OpenAI-compatible chat client with one bounded retry."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        retry_delay: float = 0.1,
    ):
        self.api_key = settings.DEEPSEEK_API_KEY if api_key is None else api_key
        self.base_url = (base_url or settings.DEEPSEEK_BASE_URL).rstrip("/")
        self.model = model or settings.DEEPSEEK_MODEL
        self.timeout = timeout or settings.DEEPSEEK_TIMEOUT_SECONDS
        self.transport = transport
        self.retry_delay = retry_delay
        self.last_usage = LLMUsage(model=self.model)

    async def request_json(self, messages: list[dict], max_tokens: int | None = None) -> LLMJSONResult:
        payload = self._payload(messages, stream=False, max_tokens=max_tokens)
        payload["response_format"] = {"type": "json_object"}
        started = perf_counter()
        response = await self._request(payload)
        data = response.json()
        try:
            content = json.loads(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise LLMClientError("DeepSeek returned invalid JSON content") from exc
        usage = self._record_usage(data.get("usage") or {}, started)
        return LLMJSONResult(content=content, usage=usage)

    async def stream_text(self, messages: list[dict], max_tokens: int | None = None) -> AsyncGenerator[str, None]:
        started = perf_counter()
        usage: dict = {}
        async for line in self._stream_lines(self._payload(messages, stream=True, max_tokens=max_tokens)):
            if not line.startswith("data:"):
                continue
            raw = line.removeprefix("data:").strip()
            if not raw or raw == "[DONE]":
                continue
            try:
                chunk = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise LLMClientError("DeepSeek returned invalid stream content") from exc
            usage.update(chunk.get("usage") or {})
            choices = chunk.get("choices") or []
            content = choices[0].get("delta", {}).get("content") if choices else None
            if content:
                yield str(content)
        self._record_usage(usage, started)

    async def _stream_lines(self, payload: dict) -> AsyncGenerator[str, None]:
        if not self.api_key:
            raise LLMClientError("DEEPSEEK_API_KEY is not configured")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        emitted = False
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(transport=self.transport, timeout=self.timeout) as client:
                    async with client.stream(
                        "POST",
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    ) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            emitted = True
                            yield line
                return
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError) as exc:
                retryable = not isinstance(exc, httpx.HTTPStatusError) or exc.response.status_code >= 500
                if emitted or attempt == 1 or not retryable:
                    raise LLMClientError(f"DeepSeek request failed: {exc}") from exc
                await asyncio.sleep(self.retry_delay)

    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            await self.request_json([{"role": "user", "content": 'Return exactly {"ok": true} as JSON.'}], max_tokens=16)
        except LLMClientError:
            return False
        return True

    def _payload(self, messages: list[dict], stream: bool, max_tokens: int | None) -> dict:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "max_tokens": max_tokens or settings.DEEPSEEK_MAX_TOKENS,
        }
        if stream:
            payload["stream_options"] = {"include_usage": True}
        return payload

    async def _request(self, payload: dict) -> httpx.Response:
        if not self.api_key:
            raise LLMClientError("DEEPSEEK_API_KEY is not configured")
        headers = {"Authorization": f"Bearer {self.api_key}"}
        for attempt in range(2):
            try:
                async with httpx.AsyncClient(transport=self.transport, timeout=self.timeout) as client:
                    response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                response.raise_for_status()
                return response
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError) as exc:
                retryable = not isinstance(exc, httpx.HTTPStatusError) or exc.response.status_code >= 500
                if attempt == 1 or not retryable:
                    raise LLMClientError(f"DeepSeek request failed: {exc}") from exc
                await asyncio.sleep(self.retry_delay)
        raise LLMClientError("DeepSeek request failed")

    def _record_usage(self, payload: dict, started: float) -> LLMUsage:
        self.last_usage = LLMUsage(
            prompt_tokens=int(payload.get("prompt_tokens") or 0),
            completion_tokens=int(payload.get("completion_tokens") or 0),
            total_tokens=int(payload.get("total_tokens") or 0),
            elapsed_ms=int((perf_counter() - started) * 1000),
            model=self.model,
        )
        return self.last_usage
