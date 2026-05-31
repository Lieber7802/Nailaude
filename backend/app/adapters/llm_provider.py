"""
LLM Provider Adapter - OpenAI-compatible API direct call.

Uses Volcano Engine / DeepSeek / OpenAI API with streaming.
Parses code blocks from LLM output and writes to project directory.
"""
import re
from typing import AsyncGenerator

import httpx

from app.adapters.base import AgentAdapter, AgentEvent
from app.services.llm_client import LLMClient, LLMClientError


FENCED_BLOCK_PATTERN = re.compile(
    r"```(?P<info>[^\n`]*)\n(?P<content>.*?)(?:\n```|$)",
    re.DOTALL,
)


class LLMProviderAdapter(AgentAdapter):
    """LLM Provider adapter - direct API call with code extraction."""

    platform_name = "llm"

    def __init__(
        self,
        client: LLMClient | httpx.AsyncClient | None = None,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
        max_tokens: int | None = None,
    ):
        # Keep the M2 AsyncClient injection surface while routing all requests
        # through the reusable M3 client.
        transport = client._transport if isinstance(client, httpx.AsyncClient) else None
        self.client = (
            client
            if isinstance(client, LLMClient)
            else LLMClient(
                api_key=api_key,
                base_url=base_url,
                model=model,
                timeout=timeout_seconds,
                transport=transport,
            )
        )
        self.max_tokens = max_tokens

    async def run_task(
        self, work_dir: str, instruction: str, context: dict
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Stream a direct DeepSeek response through the standard Agent event contract.
        """
        content_parts: list[str] = []
        try:
            async for chunk in self.client.stream_text(
                self._build_messages(instruction, context),
                max_tokens=self.max_tokens,
            ):
                content_parts.append(chunk)
                yield AgentEvent(type="text_delta", content=chunk)
        except LLMClientError as exc:
            yield AgentEvent(type="error", content=str(exc))
        for artifact in self._extract_code_artifacts("".join(content_parts)):
            yield artifact
        yield AgentEvent(type="done", content="")

    async def health_check(self) -> bool:
        return await self.client.health_check()

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
