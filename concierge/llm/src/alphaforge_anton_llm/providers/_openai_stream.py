"""OpenAI-compatible SSE streaming helper (internal, not public API)."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

import httpx

from alphaforge_anton_llm.providers._openai_compat import build_body, headers
from alphaforge_anton_llm.types import Message, ProviderResponse

logger = logging.getLogger(__name__)


async def openai_stream(
    *,
    base_url: str,
    api_key: str,
    model: str,
    provider_name: str,
    messages: list[Message],
    timeout: float = 60.0,
) -> AsyncIterator[ProviderResponse]:
    """Yield ProviderResponse snapshots with progressively-growing content."""
    body = {
        **build_body(model, messages, None),
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    content = ""
    final_model = model
    prompt_tokens = 0
    completion_tokens = 0

    async with httpx.AsyncClient(timeout=timeout) as c:
        async with c.stream(
            "POST", f"{base_url}/chat/completions", json=body, headers=headers(api_key),
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                chunk = line[6:].strip()
                if chunk == "[DONE]":
                    break
                try:
                    obj = json.loads(chunk)
                except json.JSONDecodeError:
                    continue
                final_model = obj.get("model", final_model)
                if usage := obj.get("usage"):
                    prompt_tokens = usage.get("prompt_tokens", prompt_tokens)
                    completion_tokens = usage.get("completion_tokens", completion_tokens)
                for choice in obj.get("choices") or []:
                    delta = (choice.get("delta") or {}).get("content")
                    if delta:
                        content += delta
                        yield ProviderResponse(
                            content=content,
                            provider=provider_name,
                            model=final_model,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                        )

    yield ProviderResponse(
        content=content,
        provider=provider_name,
        model=final_model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
    )
