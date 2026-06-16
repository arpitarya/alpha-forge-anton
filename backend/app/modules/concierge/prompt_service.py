"""Prompt assembly for Orff — system/grounding/memory/holdings + routing resolution
(privacy floor > vision > pin > trusted-lane thinking tier), with a UI `trace`."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from alphaforge_anton_llm import registry
from alphaforge_anton_llm.types import Message, QueryType

from app.modules.concierge.concierge_schemas import ChatRequest
from app.modules.concierge.fux_bridge import recall as fux_recall
from app.modules.concierge.holdings_private import detailed_context, enforce_floor
from app.modules.concierge.memory_service import MEMORY_PREAMBLE, load_context
from app.modules.concierge.plan_context import inject as signals_ground
from app.modules.concierge.prompt_text import GROUNDING_PREAMBLE, SYSTEM
from app.modules.concierge.tiering_service import resolve as resolve_tier
from app.modules.signals.objective_config import load_objective


@dataclass
class Assembled:
    msgs: list[Message]
    query_type: QueryType
    preferred: str | None
    confirmed: bool
    notice: str | None
    model: str | None
    last_user: str
    trace: list[dict] = field(default_factory=list)
    reasoning: bool = False  # trusted-lane extended thinking gate (Phase 4)
    effort: str | None = None
    deep_search_mode: str = "auto"  # agent-initiated deep search; consumed by the tool loop


def _step(trace: list[dict], name: str, detail: str, t: float) -> None:
    trace.append({"name": name, "detail": detail, "ms": int((time.perf_counter() - t) * 1000)})


async def assemble(req: ChatRequest) -> Assembled:
    trace: list[dict] = []
    # Cacheable prefix (turn-stable): SYSTEM → objective → memory, contiguous + flagged.
    msgs = [Message(role="system", content=SYSTEM, cacheable=True)]
    last_user = next((m.content for m in reversed(req.messages) if m.role == "user"), "")

    t = time.perf_counter()
    grounding = await fux_recall(last_user) if last_user else ""  # volatile (query-dependent)
    if grounding:
        _step(trace, "fux.recall", f"{len(grounding)} chars of project knowledge", t)
    if obj_text := load_objective().context_text():
        msgs.append(Message(role="system", content=obj_text, cacheable=True))
        _step(trace, "objective.inject", "north-star context", t)

    t = time.perf_counter()
    memory = await load_context()
    if memory:
        msgs.append(Message(role="system", content=MEMORY_PREAMBLE + memory, cacheable=True))
        _step(trace, "memory.load", f"{len(memory)} chars of user context", t)
    # ── cache breakpoint ── volatile blocks follow (per-turn): Fux, web (§9), signals (§7).
    if grounding:
        msgs.append(Message(role="system", content=GROUNDING_PREAMBLE + grounding))
    await signals_ground(req, msgs, trace)
    msgs.extend(
        Message(role=m.role, content=m.content, images=list(m.images)) for m in req.messages
    )

    # Classify on the text so a holdings query is caught even under an explicit pin:
    # private → trusted-provider floor, THEN disclose (full rows only to that lane).
    intent_qt = registry.classify_intent(last_user)
    if registry.is_private(intent_qt):
        t = time.perf_counter()
        qt, preferred, confirmed, notice = enforce_floor(req.provider, intent_qt)
        msgs.append(Message(role="system", content=detailed_context(preferred)))
        level = (
            "full rows → trusted lane"
            if preferred in registry.trusted_providers()
            else "percentages only"
        )
        _step(trace, "holdings.disclose", level, t)
    elif req.provider == "auto":
        qt, preferred = registry.classify_intent(last_user), None
        confirmed, notice = False, None
    else:
        qt, preferred = registry.provider_query_type(req.provider), req.provider
        confirmed, notice = req.provider == "claude-sdk", None

    # An attached image floors routing to a vision provider (privacy floor outranks it).
    vision = registry.vision_providers()
    if any(m.images for m in req.messages) and preferred not in vision and vision:
        if not registry.is_private(intent_qt):
            preferred, notice = vision[0], notice or "Image attached — routed to a vision provider."
            trace.append({"name": "vision.route", "detail": f"→ {vision[0]}", "ms": 0})

    # Pinned model id only when routing kept the user's provider; then the thinking tier.
    model = req.model_id if preferred == req.provider and req.provider != "auto" else None
    model, reasoning, effort = resolve_tier(req.thinking_mode, intent_qt, preferred, model)
    return Assembled(msgs, qt, preferred, confirmed, notice, model, last_user, trace,
                     reasoning, effort, req.deep_search_mode)
