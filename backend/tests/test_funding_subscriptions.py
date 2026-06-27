"""Subscriptions registry → monthly opex in INR (USD converts, annual amortizes)."""

from __future__ import annotations

from pathlib import Path

from app.modules.funding.funding_subscriptions import (
    load_subscriptions,
    opex_per_month,
    self_funding,
)

_FIXTURE = """
[[sub]]
name = "ClaudeUSD"
amount = 20.0
currency = "USD"
cadence = "monthly"

[[sub]]
name = "AnnualINR"
amount = 1200.0
currency = "INR"
cadence = "annual"
"""


def _write(tmp_path: Path) -> Path:
    p = tmp_path / "subs.toml"
    p.write_text(_FIXTURE, encoding="utf-8")
    return p


def test_load_parses_rows(tmp_path: Path) -> None:
    subs = load_subscriptions(_write(tmp_path))
    assert [s.name for s in subs] == ["ClaudeUSD", "AnnualINR"]


def test_opex_converts_usd_and_amortizes_annual(tmp_path: Path) -> None:
    opex = opex_per_month(_write(tmp_path))
    # INR row: 1200/12 = 100. USD row: 20 USD at ~83 INR is well over 1000 total.
    assert opex > 1000.0
    # The annual INR contribution alone is exactly 100/month.
    inr_only = next(s for s in load_subscriptions(_write(tmp_path)) if s.name == "AnnualINR")
    assert inr_only.monthly_inr() == 100.0


def test_missing_file_is_zero_opex(tmp_path: Path) -> None:
    assert opex_per_month(tmp_path / "nope.toml") == 0.0


def test_committed_registry_loads() -> None:
    # The real subscriptions.toml is valid and yields a non-negative opex.
    assert opex_per_month() >= 0.0


def test_covered_is_honest_pending_and_savings_never_flip_it() -> None:
    sf = self_funding(cage_savings_per_month=99_999.0)
    assert sf.covered is None  # no realised-P&L source yet (Gate-4 paper) — never a faked bool
    assert sf.cage_savings_per_month == 99_999.0  # carried as its own line, not income
    assert sf.opex_per_month == opex_per_month()  # opex unchanged by savings
