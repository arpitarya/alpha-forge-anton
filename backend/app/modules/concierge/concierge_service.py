"""Orff concierge service — streams provider tokens as SSE."""

from __future__ import annotations

import json
import re
import time

from alphaforge_anton_llm.gateway import create_gateway
from alphaforge_anton_llm.types import Message, QueryType

from app.modules.concierge.concierge_schemas import PROVIDER_TO_QUERY_TYPE, ChatMessage, ChatRequest

_SYSTEM = (
    "You are Orff, the AI financial concierge inside AlphaForge Anton — a personal investment "
    "terminal for Indian markets. Be concise, data-driven, and actionable. Format numbers in "
    "Indian locale (₹, L, Cr). When you recommend a trade, include the rationale and expected "
    "impact on the portfolio. Keep responses under 400 words unless a detailed breakdown is "
    "explicitly requested."
)

_QUERY_TYPE_BY_INTENT: list[tuple[str, QueryType]] = [
    (r"risk|drawdown|var|simulat|stress|exposure|rebalanc|hedge|tax", QueryType.INVESTMENT_PLAN),
    (r"screen|scan|breakout|filter|quote|ltp|price of|ticker", QueryType.FACTOID),
    (r"news|sector|industry|earning|result|quarterly", QueryType.NEWS_LOOKUP),
    (r"portfolio|holding|allocation|weight|sleeve", QueryType.PORTFOLIO_OVERVIEW),
]

_gateway = create_gateway()


def _resolve(req: ChatRequest, last_user_msg: str) -> tuple[QueryType, str | None]:
    if req.provider == "auto":
        for pattern, qt in _QUERY_TYPE_BY_INTENT:
            if re.search(pattern, last_user_msg, re.IGNORECASE):
                return qt, None
        return QueryType.MULTI_TURN, None
    qt_slug = PROVIDER_TO_QUERY_TYPE.get(req.provider, "factoid")
    return QueryType(qt_slug), req.provider


def _sse(payload: dict) -> bytes:
    return f"data: {json.dumps(payload)}\n\n".encode()


async def stream_chat(req: ChatRequest):
    """Async generator yielding SSE-formatted bytes per token snapshot."""
    msgs = [Message(role="system", content=_SYSTEM)]
    msgs.extend(Message(role=m.role, content=m.content) for m in req.messages)

    last_user = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
    qt, preferred = _resolve(req, last_user)
    confirmed = req.provider == "claude-sdk"

    t0 = time.perf_counter()
    try:
        async for snap in _gateway.stream(
            msgs, query_type=qt, preferred_provider=preferred, confirmed=confirmed,
        ):
            yield _sse({
                "content": snap.content,
                "provider": snap.provider,
                "model": snap.model,
                "prompt_tokens": snap.prompt_tokens,
                "completion_tokens": snap.completion_tokens,
                "elapsed_s": round(time.perf_counter() - t0, 2),
                "auto_level": req.auto_level,
            })
    except Exception as exc:
        yield _sse({"error": str(exc), "elapsed_s": round(time.perf_counter() - t0, 2)})
    finally:
        yield b"data: [DONE]\n\n"


__all__ = ["ChatMessage", "stream_chat"]
