"""Orff component composition — generate a declarative UISpec from a prompt,
validated against the Fux registry before it reaches the client (§18.3).

Safe by construction: the model emits JSON describing a tree of *registry*
components; Fux validates it; the frontend renders from a whitelist. No code is
generated or executed. One repair round is allowed on validation failure."""

from __future__ import annotations

import json
import re

from alphaforge_anton_llm.gateway import create_gateway
from alphaforge_anton_llm.types import Message, QueryType

from app.modules.concierge import fux_bridge
from app.modules.concierge.compose_prompt import build_system
from app.modules.concierge.compose_registry import composable_errors, narrow_registry
from app.modules.concierge.compose_schemas import ComposeRequest, ComposeResponse

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)
_gateway = create_gateway()


def _extract(text: str) -> dict:
    m = _FENCE.search(text)
    return json.loads(m.group(1) if m else text)


async def compose(req: ComposeRequest) -> ComposeResponse:
    reg = narrow_registry(await fux_bridge.registry())
    preferred = None if req.provider == "auto" else req.provider
    msgs = [Message(role="system", content=build_system(reg)),
            Message(role="user", content=req.prompt)]
    last: ComposeResponse | None = None
    for attempt in (1, 2):
        r = await _gateway.complete(msgs, query_type=QueryType.FACTOID,
                                    preferred_provider=preferred)
        try:
            spec = _extract(r.content)
        except (ValueError, json.JSONDecodeError):
            last = ComposeResponse(spec=None, valid=False, provider=r.provider,
                                   model=r.model, attempts=attempt,
                                   errors=["model did not return valid JSON"])
            continue
        ok, errs = await fux_bridge.validate(spec)
        comp_errs = composable_errors(spec)  # narrower than the fux registry check
        ok, errs = ok and not comp_errs, errs + comp_errs
        last = ComposeResponse(spec=spec, valid=ok, errors=errs, provider=r.provider,
                               model=r.model, attempts=attempt)
        if ok:
            break
        msgs.append(Message(role="assistant", content=r.content))
        msgs.append(Message(role="user", content=(
            "The validator rejected that spec:\n" + "\n".join(errs) +
            "\nReturn corrected JSON using ONLY the listed components, props, and hooks.")))
    await fux_bridge.record_feedback({"prompt": req.prompt, **last.model_dump(
        include={"valid", "errors", "attempts", "provider", "model"})})
    return last  # type: ignore[return-value]


async def compose_followup(prompt: str) -> dict | None:
    """Chat-stream hook: a `{spec, spec_provider}` SSE payload when the turn asks
    for UI (`registry.wants_compose`, manifest-driven), else None. Best-effort —
    failures and invalid specs return None; the text answer already streamed."""
    from alphaforge_anton_llm import registry

    if not registry.wants_compose(prompt):
        return None
    try:
        r = await compose(ComposeRequest(prompt=prompt))
    except Exception:
        return None
    return {"spec": r.spec, "spec_provider": r.provider} if r.valid and r.spec else None
