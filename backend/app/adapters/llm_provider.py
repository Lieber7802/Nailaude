"""
LLM Provider Adapter - OpenAI-compatible API direct call.

Uses Volcano Engine / DeepSeek / OpenAI API with streaming.
Parses code blocks from LLM output and writes to project directory.
"""
import json
import os
import re
from typing import AsyncGenerator

import httpx

from app.adapters.base import AgentAdapter, AgentEvent
from app.config import settings


FENCED_BLOCK_PATTERN = re.compile(
    r"```(?P<info>[^\n`]*)\n(?P<content>.*?)(?:\n```|$)",
    re.DOTALL,
)


class LLMProviderAdapter(AgentAdapter):
    """LLM Provider adapter - direct API call with code extraction."""

    platform_name = "llm"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
        max_tokens: int | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        self.api_key = api_key if api_key is not None else os.getenv("DEEPSEEK_API_KEY", settings.DEEPSEEK_API_KEY)
        self.base_url = (base_url or os.getenv("DEEPSEEK_BASE_URL", settings.DEEPSEEK_BASE_URL)).rstrip("/")
        self.model = model or os.getenv("DEEPSEEK_MODEL", settings.DEEPSEEK_MODEL)
        self.timeout_seconds = timeout_seconds or settings.DEEPSEEK_TIMEOUT_SECONDS
        self.max_tokens = max_tokens or settings.DEEPSEEK_MAX_TOKENS
        self._client = client

    async def run_task(
        self, work_dir: str, instruction: str, context: dict
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Call DeepSeek through its OpenAI-compatible streaming API.
        """
        if not self.api_key:
            yield AgentEvent(type="error", content="DEEPSEEK_API_KEY is not configured")
            yield AgentEvent(type="done", content="")
            return

        content_parts: list[str] = []
        owns_client = self._client is None
        client = self._client or httpx.AsyncClient(timeout=self.timeout_seconds)
        try:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": self._build_messages(instruction, context),
                    "stream": True,
                    "max_tokens": self.max_tokens,
                },
            ) as response:
                if response.status_code >= 400:
                    detail = await response.aread()
                    yield AgentEvent(
                        type="error",
                        content=f"DeepSeek API error {response.status_code}: {detail.decode(errors='ignore')}",
                    )
                    yield AgentEvent(type="done", content="")
                    return

                async for line in response.aiter_lines():
                    chunk = self._parse_sse_line(line)
                    if chunk is None:
                        continue
                    if chunk == "[DONE]":
                        break
                    delta = self._extract_delta(chunk)
                    if delta:
                        content_parts.append(delta)
                        yield AgentEvent(type="text_delta", content=delta)
        except httpx.HTTPError as exc:
            yield AgentEvent(type="error", content=f"DeepSeek request failed: {exc}")
            yield AgentEvent(type="done", content="")
            return
        finally:
            if owns_client:
                await client.aclose()

        for artifact in self._extract_code_artifacts("".join(content_parts)):
            yield artifact
        yield AgentEvent(type="done", content="")

    async def health_check(self) -> bool:
        return bool(self.api_key)

    def _build_messages(self, instruction: str, context: dict) -> list[dict[str, str]]:
        system_instruction = str(
            context.get("systemInstruction")
            or context.get("system_instruction")
            or "You are an AgentHub assistant. Return concise, useful results."
        )
        agent_name = context.get("agentName") or context.get("agent_name")
        if agent_name:
            system_instruction = f"{system_instruction}\nCurrent agent role: {agent_name}."
        return [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": instruction},
        ]

    def _parse_sse_line(self, line: str) -> str | None:
        if not line or not line.startswith("data:"):
            return None
        return line.removeprefix("data:").strip()

    def _extract_delta(self, raw_data: str) -> str:
        try:
            payload = json.loads(raw_data)
        except json.JSONDecodeError:
            return ""
        choices = payload.get("choices") or []
        if not choices:
            return ""
        delta = choices[0].get("delta") or {}
        return str(delta.get("content") or "")

    def _extract_code_artifacts(self, content: str) -> list[AgentEvent]:
        artifacts: list[AgentEvent] = []
        for index, match in enumerate(FENCED_BLOCK_PATTERN.finditer(content), start=1):
            info = match.group("info").strip()
            code = match.group("content").strip()
            if not code:
                continue
            language, filename = self._parse_fence_info(info, index)
            artifacts.append(
                AgentEvent(
                    type="file_created",
                    content=filename,
                    metadata={
                        "title": filename,
                        "files": [{"name": filename, "content": code, "language": language}],
                        "previewUrl": None,
                    },
                )
            )
        return artifacts

    def _parse_fence_info(self, info: str, index: int) -> tuple[str, str]:
        parts = [part.strip() for part in info.split() if part.strip()]
        language = parts[0] if parts else "text"
        filename = next((part for part in parts[1:] if "/" in part or "." in part), "")
        if not filename:
            extension = {"javascript": "js", "typescript": "ts", "python": "py"}.get(language, language)
            filename = f"llm-output-{index}.{extension or 'txt'}"
        return language, filename
