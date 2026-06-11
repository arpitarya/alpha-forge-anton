"""Gemini adapter — free tier, long context, good for portfolio_overview."""

from __future__ import annotations

import logging
import os
from typing import AsyncIterator

import httpx

from alphaforge_anton_llm import pricing
from alphaforge_anton_llm.providers.base import ProviderAdapter, ProviderHealth
from alphaforge_anton_llm.types import Message, ProviderResponse, ToolSchema

logger = logging.getLogger(__name__)

_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


def _to_gemini_contents(messages: list[Message]) -> list[dict]:
    role_map = {"user": "user", "assistant": "model", "system": "user"}
    return [
        {"role": role_map.get(m.role, "user"), "parts": [{"text": m.content}]}
        for m in messages if m.role != "tool"
    ]


class GeminiAdapter(ProviderAdapter):
    name = "gemini"
    env_key = "GEMINI_API_KEY"
    supports_tool_calling = False  # REST path; Phase 7 adds function declarations
    supports_streaming = False

    def __init__(self) -> None:
        self._last_error: str | None = None

    async def complete(
        self,
        messages: list[Message],
        tools: list[ToolSchema] | None = None,
        stream: bool = False,
        model: str | None = None,
    ) -> ProviderResponse | AsyncIterator[str]:
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        model = model or self.default_model()
        body = {
            "contents": _to_gemini_contents(messages),
            "generationConfig": {"maxOutputTokens": pricing.max_tokens(self.name, model)},
        }
        url = f"{_BASE}/{model}:generateContent?key={api_key}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as c:
                resp = await c.post(url, json=body)
                resp.raise_for_status()
                data = resp.json()
            self._last_error = None
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("Gemini error: %s", exc)
            raise

        text = data["candidates"][0]["content"]["parts"][0].get("text", "")
        usage = data.get("usageMetadata", {})
        return ProviderResponse(
            content=text, provider=self.name, model=model,
            prompt_tokens=usage.get("promptTokenCount", 0),
            completion_tokens=usage.get("candidatesTokenCount", 0),
            raw=data,
        )

    async def health(self) -> ProviderHealth:
        if not os.getenv("GEMINI_API_KEY"):
            return self._err("GEMINI_API_KEY not set")
        if self._last_error:
            return self._err(self._last_error)
        return self._ok()
