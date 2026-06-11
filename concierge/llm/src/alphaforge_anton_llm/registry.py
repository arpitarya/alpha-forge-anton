"""Single source of truth for concierge providers + routing.

Reads the JSON manifest that ships inside this package (`registry/`). Both the
gateway `QueryRouter` and the backend concierge module consume this — the
frontend regenerates `concierge.registry.generated.ts` from the same files. See
Fux rule `concierge-registry-single-source`.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from importlib.resources import files

from alphaforge_anton_llm.types import QueryType

_PKG = "alphaforge_anton_llm"


def _load(name: str) -> dict:
    return json.loads((files(_PKG) / "registry" / name).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _providers() -> dict:
    return _load("providers.json")


@lru_cache(maxsize=1)
def _routing() -> dict:
    return _load("routing.json")


@lru_cache(maxsize=1)
def _intents() -> list[tuple[re.Pattern[str], QueryType]]:
    return [
        (re.compile(i["pattern"], re.IGNORECASE), QueryType(i["query_type"]))
        for i in _routing()["intents"]
    ]


def load_providers() -> dict:
    """The full provider→metadata map (`{slug: {name, vendor, glyph, desc, models}}`)."""
    return _providers()["providers"]


def provider_order() -> list[str]:
    """Provider slugs in display order."""
    return list(_providers()["order"])


def provider_slugs() -> set[str]:
    """All known provider slugs (excludes the `auto` router pseudo-slug)."""
    return set(_providers()["providers"])


def default_model(slug: str) -> str:
    """A provider's default model id — the first entry in its model list."""
    return load_providers()[slug]["models"][0]["id"]


def classify_intent(text: str) -> QueryType:
    """Map free-text query → QueryType (first matching pattern wins)."""
    for pattern, qt in _intents():
        if pattern.search(text or ""):
            return qt
    return QueryType(_routing()["fallback_query_type"])


def chain_for(qt: QueryType) -> list[str]:
    """Provider fallback chain for a QueryType."""
    return list(_routing()["chains"].get(qt.value, ["gemini", "groq"]))


def provider_query_type(slug: str) -> QueryType:
    """The QueryType a pinned provider maps to for chain selection."""
    return QueryType(_routing()["provider_query_type"].get(slug, "factoid"))


def _private() -> dict:
    return _routing().get("private", {})


def private_query_types() -> set[str]:
    """QueryTypes that touch the user's real holdings — see `secure-holdings-plan`."""
    return set(_private().get("query_types", []))


def trusted_providers() -> set[str]:
    """The only providers allowed to receive a private (holdings-bearing) query."""
    return set(_private().get("trusted_providers", []))


def is_private(qt: QueryType) -> bool:
    """True when a query touches real holdings → trusted-provider floor + disclosure."""
    return qt.value in private_query_types()


def chains() -> dict[str, list[str]]:
    """All QueryType→chain mappings."""
    return {k: list(v) for k, v in _routing()["chains"].items()}


def default_policy() -> dict:
    """Scoring weights for `default_choice` / the frontend default picker."""
    return _routing()["default_policy"]


def default_choice() -> dict[str, str]:
    """The pinned default model — highest-scored across all providers.

    Priority: cost (free first) → tag → context length → provider order. Mirrors
    the frontend `pickDefaultChoice`; see Fux rule `concierge-default-model`.
    """
    policy = default_policy()
    cost_score: dict[str, int] = policy["cost_score"]
    tag_score: dict[str, int] = policy["tag_score"]
    order = provider_order()

    def ctx_score(ctx: str) -> float:
        m = re.search(r"([\d.]+)\s*([mk])", ctx, re.IGNORECASE)
        if not m:
            return 0.0
        n = float(m.group(1))
        return n * 1000 if m.group(2).lower() == "m" else n

    best: dict[str, str] | None = None
    best_score = -1.0
    providers = load_providers()
    for slug in order:
        for m in providers[slug]["models"]:
            score = (
                cost_score.get(m["cost"], 0) * 1e6
                + tag_score.get(m["tag"], 0) * 1e4
                + ctx_score(m["ctx"])
                + (len(order) - order.index(slug))
            )
            if score > best_score:
                best_score = score
                best = {"provider": slug, "model": m["id"]}
    return best or {"provider": "gemini", "model": "gemini-flash-latest"}
