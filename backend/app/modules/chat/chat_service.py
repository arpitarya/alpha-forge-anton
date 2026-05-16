"""Alpha chat service — routes model choice to LLMGateway and streams SSE."""

from __future__ import annotations

import json
import re
import time

from alphaforge_llm.gateway import create_gateway
from alphaforge_llm.types import Message, QueryType

from app.modules.chat.chat_schemas import ChatMessage, PROVIDER_TO_QUERY_TYPE

_SYSTEM = (
    "You are Alpha, the AI financial analyst inside AlphaForge — a personal investment terminal "
    "for Indian markets. Be concise, data-driven, and actionable. Format numbers in Indian locale "
    "(₹, L, Cr). When you recommend a trade, include the rationale and expected impact on the "
    "portfolio. Keep responses under 400 words unless a detailed breakdown is explicitly requested."
)

_QUERY_TYPE_BY_INTENT: list[tuple[str, QueryType]] = [
    (r"risk|drawdown|var|simulat|scenario|stress|exposure|rebalanc|hedge|tax|optim", QueryType.INVESTMENT_PLAN),
    (r"screen|scan|breakout|filter|quote|ltp|price of|list|ticker|search",           QueryType.FACTOID),
    (r"news|sector|industry|earning|result|quarterly",                                QueryType.NEWS_LOOKUP),
    (r"portfolio|holding|allocation|weight|sleeve",                                   QueryType.PORTFOLIO_OVERVIEW),
]

_gateway = create_gateway()


def _resolve(model: str, last_user_msg: str) -> tuple[QueryType, str | None]:
    """Return (query_type, preferred_provider). preferred_provider is None for auto."""
    if model == "auto":
        for pattern, qt in _QUERY_TYPE_BY_INTENT:
            if re.search(pattern, last_user_msg, re.IGNORECASE):
                return qt, None
        return QueryType.MULTI_TURN, None

    qt_slug = PROVIDER_TO_QUERY_TYPE.get(model, "factoid")
    return QueryType(qt_slug), model


async def stream_chat(messages: list[ChatMessage], model: str):
    """Async generator yielding SSE-formatted bytes."""
    gateway_msgs = [Message(role="system", content=_SYSTEM)]
    for m in messages:
        gateway_msgs.append(Message(role=m.role, content=m.content))

    last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
    qt, preferred = _resolve(model, last_user)

    t0 = time.perf_counter()
    try:
        resp = await _gateway.complete(
            gateway_msgs,
            query_type=qt,
            preferred_provider=preferred,
        )
        elapsed = round(time.perf_counter() - t0, 2)
        payload = {
            "content": resp.content,
            "provider": resp.provider,
            "model": resp.model,
            "prompt_tokens": resp.prompt_tokens,
            "completion_tokens": resp.completion_tokens,
            "elapsed_s": elapsed,
        }
        yield f"data: {json.dumps(payload)}\n\n".encode()
    except Exception as exc:
        err = {"error": str(exc)}
        yield f"data: {json.dumps(err)}\n\n".encode()
    finally:
        yield b"data: [DONE]\n\n"
