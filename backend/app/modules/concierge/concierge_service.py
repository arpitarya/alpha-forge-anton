"""Orff concierge service — streams provider tokens and typed SSE events.

Wire protocol (one JSON object per `data:` line — concierge/README.md §events):
  {content, provider, model, …, cost_usd}  cumulative token snapshot
  {tool: {name, detail, ms}}               prompt-assembly / data-read step
  {thinking: "…"}                          reasoning trace split from <think>
  {confirm: {id, action, summary, steps}}  approval card for mutating intents
  {spec: {…}}                              compose follow-up UISpec
  {followups: ["…"]}                       tap-to-send next prompts
  {error: "…"} / [DONE]
"""

from __future__ import annotations

import time

from alphaforge_anton_llm import pricing
from alphaforge_anton_llm.gateway import create_gateway

from app.modules.concierge.action_service import detect_action
from app.modules.concierge.compose_service import compose_followup
from app.modules.concierge.concierge_schemas import ChatMessage, ChatRequest
from app.modules.concierge.followup_service import suggest_followups
from app.modules.concierge.prompt_service import assemble
from app.modules.concierge.stream_events import redact, split_thinking, sse

_gateway = create_gateway()


async def stream_chat(req: ChatRequest):
    """Async generator yielding SSE-formatted bytes per token snapshot / event."""
    # Everything lives inside the try: an exception before the first yield would kill
    # the SSE connection after the 200 headers — the browser sees only "Failed to fetch".
    t0 = time.perf_counter()

    def el() -> float:
        return round(time.perf_counter() - t0, 2)

    try:
        a = await assemble(req)
        for step in a.trace:
            yield sse({"tool": step, "elapsed_s": el()})

        snap = None
        async for snap in _gateway.stream(
            a.msgs, query_type=a.query_type, preferred_provider=a.preferred,
            model=a.model, confirmed=a.confirmed,
        ):
            thinking, visible = split_thinking(snap.content)
            if thinking:
                yield sse({"thinking": thinking, "elapsed_s": el()})
            yield sse({
                "content": visible, "provider": snap.provider, "model": snap.model,
                "prompt_tokens": snap.prompt_tokens,
                "completion_tokens": snap.completion_tokens,
                "cost_usd": round(pricing.estimate_cost_usd(
                    snap.provider, snap.model, snap.prompt_tokens, snap.completion_tokens,
                ), 6),
                "elapsed_s": el(), "auto_level": req.auto_level, "notice": a.notice,
            })

        if (action := detect_action(a.last_user)) is not None:
            yield sse({"confirm": action, "elapsed_s": el()})
        # "show / chart / …" turns also get a generated UI — additive, never an error.
        if (extra := await compose_followup(a.last_user)) is not None:
            yield sse({**extra, "elapsed_s": el()})
        reply = split_thinking(snap.content)[1] if snap else ""
        if chips := await suggest_followups(_gateway, a.last_user, reply):
            yield sse({"followups": chips, "elapsed_s": el()})
    except Exception as exc:
        yield sse({"error": redact(str(exc)), "elapsed_s": el()})
    finally:
        yield b"data: [DONE]\n\n"


__all__ = ["ChatMessage", "stream_chat"]
