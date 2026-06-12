"""Orff concierge service — streams provider tokens as SSE."""

from __future__ import annotations

import json
import re
import time

from alphaforge_anton_llm import registry
from alphaforge_anton_llm.gateway import create_gateway
from alphaforge_anton_llm.types import Message, QueryType

from app.modules.concierge.compose_service import compose_followup
from app.modules.concierge.concierge_schemas import ChatMessage, ChatRequest
from app.modules.concierge.fux_bridge import recall as fux_recall
from app.modules.concierge.holdings_private import disclosed_context, enforce_floor

_SYSTEM = (
    "You are Orff, the AI financial concierge inside AlphaForge Anton — a personal investment "
    "terminal for Indian markets. Be concise, data-driven, and actionable. Format numbers in "
    "Indian locale (₹, L, Cr). When you recommend a trade, include the rationale and expected "
    "impact on the portfolio. Keep responses under 400 words unless a detailed breakdown is "
    "explicitly requested."
)
_GROUNDING_PREAMBLE = (
    "Authoritative project knowledge from Fux (Anton's knowledge brain). Treat these "
    "rules, formulas, and definitions as ground truth when they apply; cite the figures "
    "and logic they prescribe rather than inventing your own:\n\n"
)

_gateway = create_gateway()


def _resolve(req: ChatRequest, last_user_msg: str) -> tuple[QueryType, str | None]:
    # Intent → QueryType lives in the registry manifest (concierge-registry-single-source).
    if req.provider == "auto":
        return registry.classify_intent(last_user_msg), None
    return registry.provider_query_type(req.provider), req.provider


def _sse(payload: dict) -> bytes:
    return f"data: {json.dumps(payload)}\n\n".encode()


# Upstream provider errors embed the request URL, which carries the API key as a
# `?key=…`/`?api_key=…` query param. Never forward a live secret to the browser.
_SECRET_RE = re.compile(r"(?i)([?&](?:api[_-]?key|key|token|access_token)=)[^&\s\"']+")


def _redact(msg: str) -> str:
    return _SECRET_RE.sub(r"\1<redacted>", msg)


async def stream_chat(req: ChatRequest):
    """Async generator yielding SSE-formatted bytes per token snapshot."""
    msgs = [Message(role="system", content=_SYSTEM)]
    last_user = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
    grounding = await fux_recall(last_user) if last_user else ""
    if grounding:
        msgs.append(Message(role="system", content=_GROUNDING_PREAMBLE + grounding))
    msgs.extend(Message(role=m.role, content=m.content) for m in req.messages)

    # Classify on the text so a holdings query is caught even under an explicit pin:
    # private → inject percentages-only context + force the trusted-provider floor.
    intent_qt = registry.classify_intent(last_user)
    if registry.is_private(intent_qt):
        msgs.append(Message(role="system", content=disclosed_context()))
        qt, preferred, confirmed, notice = enforce_floor(req.provider, intent_qt)
    else:
        qt, preferred = _resolve(req, last_user)
        confirmed, notice = req.provider == "claude-sdk", None

    # Honour the pinned model id only when routing kept the user's provider (the privacy
    # floor or Auto can override it; a foreign model id must not leak onto another provider).
    model = req.model_id if preferred == req.provider and req.provider != "auto" else None
    t0 = time.perf_counter()
    try:
        async for snap in _gateway.stream(
            msgs, query_type=qt, preferred_provider=preferred, model=model, confirmed=confirmed,
        ):
            yield _sse({
                "content": snap.content,
                "provider": snap.provider,
                "model": snap.model,
                "prompt_tokens": snap.prompt_tokens,
                "completion_tokens": snap.completion_tokens,
                "elapsed_s": round(time.perf_counter() - t0, 2),
                "auto_level": req.auto_level,
                "notice": notice,
            })
        # "show / chart / …" turns also get a generated UI — additive, never an error.
        if (extra := await compose_followup(last_user)) is not None:
            yield _sse({**extra, "elapsed_s": round(time.perf_counter() - t0, 2)})
    except Exception as exc:
        yield _sse({"error": _redact(str(exc)), "elapsed_s": round(time.perf_counter() - t0, 2)})
    finally:
        yield b"data: [DONE]\n\n"


__all__ = ["ChatMessage", "stream_chat"]
