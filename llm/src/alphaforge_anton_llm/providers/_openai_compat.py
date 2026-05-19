"""Shared OpenAI-compatible completion helper (internal, not public API)."""

from __future__ import annotations

import json
import logging

import httpx

from alphaforge_anton_llm.types import Message, ProviderResponse, ToolCall, ToolSchema

logger = logging.getLogger(__name__)


async def openai_complete(
    *,
    base_url: str,
    api_key: str,
    model: str,
    provider_name: str,
    messages: list[Message],
    tools: list[ToolSchema] | None = None,
    timeout: float = 30.0,
) -> ProviderResponse:
    body: dict = {
        "model": model,
        "messages": [m.model_dump(exclude_none=True) for m in messages],
    }
    if tools:
        body["tools"] = [
            {"type": "function", "function": t.model_dump()} for t in tools
        ]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=timeout) as c:
        resp = await c.post(f"{base_url}/chat/completions", json=body, headers=headers)
        if resp.status_code == 429:
            import asyncio as _a
            delay = float(resp.headers.get("Retry-After", "1") or 1)
            await _a.sleep(min(delay, 3.0))
            resp = await c.post(f"{base_url}/chat/completions", json=body, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    choice = data["choices"][0]
    msg = choice["message"]
    tool_calls = [
        ToolCall(
            call_id=tc["id"],
            name=tc["function"]["name"],
            args=json.loads(tc["function"]["arguments"]),
        )
        for tc in (msg.get("tool_calls") or [])
    ]
    return ProviderResponse(
        content=msg.get("content") or "",
        provider=provider_name,
        model=data.get("model", model),
        prompt_tokens=data.get("usage", {}).get("prompt_tokens", 0),
        completion_tokens=data.get("usage", {}).get("completion_tokens", 0),
        tool_calls=tool_calls,
        raw=data,
    )
