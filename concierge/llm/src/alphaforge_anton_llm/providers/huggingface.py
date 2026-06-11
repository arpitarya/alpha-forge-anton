"""HuggingFace Inference API adapter — free serverless models, no tool calling."""

from __future__ import annotations

import logging
import os
from typing import AsyncIterator

import httpx

from alphaforge_anton_llm import pricing
from alphaforge_anton_llm.providers.base import ProviderAdapter, ProviderHealth
from alphaforge_anton_llm.types import Message, ProviderResponse, ToolSchema

logger = logging.getLogger(__name__)

_BASE = "https://api-inference.huggingface.co/models"


def _build_prompt(messages: list[Message]) -> str:
    parts = []
    for m in messages:
        if m.role == "system":
            parts.append(f"<s>[INST] <<SYS>>\n{m.content}\n<</SYS>>\n\n")
        elif m.role == "user":
            parts.append(f"{m.content} [/INST] ")
        elif m.role == "assistant":
            parts.append(f"{m.content} </s><s>[INST] ")
    return "".join(parts)


class HuggingFaceAdapter(ProviderAdapter):
    name = "huggingface"
    env_key = "HF_API_KEY"
    supports_tool_calling = False
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
        api_key = os.getenv("HF_API_KEY", "")
        if not api_key:
            raise RuntimeError("HF_API_KEY not set")
        model = model or self.default_model()
        headers = {"Authorization": f"Bearer {api_key}"}
        max_new = pricing.max_tokens(self.name, model)
        body = {"inputs": _build_prompt(messages), "parameters": {"max_new_tokens": max_new}}
        try:
            async with httpx.AsyncClient(timeout=60.0) as c:
                resp = await c.post(f"{_BASE}/{model}", json=body, headers=headers)
                resp.raise_for_status()
                data = resp.json()
            self._last_error = None
        except Exception as exc:
            self._last_error = str(exc)
            logger.warning("HuggingFace error: %s", exc)
            raise

        text = data[0].get("generated_text", "") if isinstance(data, list) else str(data)
        return ProviderResponse(
            content=text, provider=self.name, model=model, raw={"response": data},
        )

    async def health(self) -> ProviderHealth:
        if not os.getenv("HF_API_KEY"):
            return self._err("HF_API_KEY not set")
        if self._last_error:
            return self._err(self._last_error)
        return self._ok()
