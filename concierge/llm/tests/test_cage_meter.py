"""cage_meter adapter — records completions into the Cage ledger, fail-open."""

from __future__ import annotations

import pytest

from alphaforge_anton_llm import cage_meter
from alphaforge_anton_llm.types import ProviderResponse, QueryType

cage = pytest.importorskip("cage")  # skip if the sibling flux isn't installed


@pytest.fixture
def ledger_dir(tmp_path, monkeypatch):
    """Redirect the Cage ledger to a temp dir via CAGE_LEDGER (honoured by Footprint)."""
    d = tmp_path / "ledger"
    monkeypatch.setenv("CAGE_LEDGER", str(d))
    return d


def _resp(model: str, tin: int, tout: int) -> ProviderResponse:
    return ProviderResponse(content="x", provider="claude-sdk", model=model,
                            prompt_tokens=tin, completion_tokens=tout)


def test_record_writes_a_call_with_route_and_cost(ledger_dir):
    cage_meter.record(_resp("claude-opus-4-8", 8600, 1500),
                      query_type=QueryType.INVESTMENT_PLAN, latency_ms=5120, session="s1")
    (call,) = cage.ledger.calls(cage_meter._ROOT)
    assert call["route"] == "investment_plan"
    assert call["agent"] == "orff"
    assert call["model"] == "claude-opus-4-8"
    assert call["latency_ms"] == 5120
    # Anton pricing: 8600·$15/M in + 1500·$75/M out = $0.2415.
    assert call["est_cost_usd"] == pytest.approx(0.2415, abs=1e-4)


def test_record_is_fail_open_on_bad_input(ledger_dir, monkeypatch):
    # A ProviderResponse the pricing layer can't price must not raise out of record().
    monkeypatch.setattr(cage_meter.pricing, "estimate_cost_usd",
                        lambda *a, **k: (_ for _ in ()).throw(KeyError("no price")))
    cage_meter.record(_resp("ghost-model", 10, 10), query_type=QueryType.FACTOID)
    assert cage.ledger.calls(cage_meter._ROOT) == []  # nothing recorded, nothing raised
