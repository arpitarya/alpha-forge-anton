"""Per-model consumption + cost — read from the registry manifest.

Every model in `registry/providers.json` carries a `consumption` block
(`input_per_m`, `output_per_m`, `max_tokens`, `paid`). This module is the single
place that interprets it: CostGuard reads `is_paid`, adapters read `max_tokens`,
and `estimate_cost_usd` turns a `ProviderResponse`'s token counts into real spend.
Add or reprice a model by editing the JSON — never hardcode pricing in code. See
Fux rule `concierge-registry-single-source`.
"""

from __future__ import annotations

from alphaforge_anton_llm import registry

_DEFAULT = {"input_per_m": 0.0, "output_per_m": 0.0, "max_tokens": 2048, "paid": False}


def model_meta(slug: str, model_id: str | None = None) -> dict:
    """The full metadata dict for a provider's model (defaults to its first model)."""
    models = registry.load_providers()[slug]["models"]
    target = model_id or registry.default_model(slug)
    return next((m for m in models if m["id"] == target), models[0])


def consumption(slug: str, model_id: str | None = None) -> dict:
    """The `consumption` block for a model, with safe defaults if absent."""
    return {**_DEFAULT, **model_meta(slug, model_id).get("consumption", {})}


def is_paid(slug: str, model_id: str | None = None) -> bool:
    """True when invoking this model costs real money (CostGuard gate)."""
    return bool(consumption(slug, model_id)["paid"])


def max_tokens(slug: str, model_id: str | None = None) -> int:
    """The output-token cap an adapter should send for this model."""
    return int(consumption(slug, model_id)["max_tokens"])


def estimate_cost_usd(slug: str, model_id: str | None, prompt: int, completion: int) -> float:
    """Real USD spend for a call from its prompt/completion token counts."""
    c = consumption(slug, model_id)
    return (prompt * c["input_per_m"] + completion * c["output_per_m"]) / 1_000_000
