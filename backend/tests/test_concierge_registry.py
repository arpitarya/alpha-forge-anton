"""Backend test: the concierge registry manifest is internally consistent.

Guards the single source of truth (Fux: concierge-registry-single-source) — every
routing chain references a real provider, every provider is usable, the pinned
default resolves to a real model, and intent classification behaves as specified.
"""

from typing import get_args

import pytest
from alphaforge_anton_llm import registry
from alphaforge_anton_llm.types import QueryType

from app.modules.concierge.concierge_schemas import ProviderSlug


def test_every_provider_has_at_least_one_model():
    providers = registry.load_providers()
    assert providers, "registry has no providers"
    for slug, meta in providers.items():
        assert meta["models"], f"{slug} has no models"


def test_chains_reference_known_providers():
    known = registry.provider_slugs()
    for qt, chain in registry.chains().items():
        assert chain, f"chain {qt} is empty"
        for provider in chain:
            assert provider in known, f"chain {qt} references unknown provider {provider}"


def test_provider_query_type_maps_to_real_chains():
    for slug in registry.provider_slugs():
        qt = registry.provider_query_type(slug)
        assert isinstance(qt, QueryType)
        assert registry.chain_for(qt), f"{slug} → {qt} has no chain"


def test_default_choice_resolves_to_a_real_model():
    choice = registry.default_choice()
    providers = registry.load_providers()
    assert choice["provider"] in providers
    model_ids = {m["id"] for m in providers[choice["provider"]]["models"]}
    assert choice["model"] in model_ids
    # Free + fast + long-context → Gemini Flash today.
    assert choice == {"provider": "gemini", "model": "gemini-flash-latest"}


def test_provider_slug_literal_matches_registry():
    assert set(get_args(ProviderSlug)) == registry.provider_slugs() | {"auto"}


@pytest.mark.parametrize(
    "text,expected",
    [
        # Anything touching the user's real holdings classifies private (→ trusted floor).
        ("show my risk exposure and rebalance", QueryType.PORTFOLIO_PRIVATE),
        ("portfolio allocation by sleeve", QueryType.PORTFOLIO_PRIVATE),
        # Educational / analytical, not holdings-bearing → free providers are fine.
        ("how does tax-loss harvesting work", QueryType.INVESTMENT_PLAN),
        ("latest sector news today", QueryType.NEWS_LOOKUP),
        ("screen breakouts under 500", QueryType.FACTOID),
        ("hello, how are you", QueryType.MULTI_TURN),
        ("", QueryType.MULTI_TURN),
    ],
)
def test_classify_intent(text: str, expected: QueryType):
    assert registry.classify_intent(text) == expected


def test_private_queries_route_only_to_trusted_providers():
    """The security floor: every private query-type's whole chain is a trusted provider."""
    trusted = registry.trusted_providers()
    assert trusted, "no trusted providers configured for private routing"
    for qt_slug in registry.private_query_types():
        chain = registry.chains().get(qt_slug, [])
        assert chain, f"private query-type {qt_slug} has no chain"
        assert set(chain) <= trusted, f"{qt_slug} chain {chain} escapes the trusted floor"
