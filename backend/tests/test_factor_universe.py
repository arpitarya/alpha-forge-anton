"""factor_universe.liquid_as_of — point-in-time liquidity membership, fallback, exclusions."""

from __future__ import annotations

import pytest

from app.modules.edges import factor_universe as fu
from app.modules.edges.factor_panel import Panel

_DATES = [f"2024-01-{i + 1:02d}" for i in range(5)]


@pytest.fixture(autouse=True)
def _reset_exclusions():
    prev = fu.set_active(fu.Exclusions())  # isolate global state per test
    yield
    fu.set_active(prev)


def _panel(
    turnover: dict[str, list[float]] | None = None, closes: dict[str, list[float]] | None = None
) -> Panel:
    closes = closes or {s: [10.0] * 5 for s in ("AAA", "BBB", "CCC", "DDD")}
    return Panel(dates=_DATES, closes=closes, nifty=[1.0] * 5, turnover=turnover or {})


def test_fallback_to_full_universe_when_no_turnover() -> None:
    # Synthetic panel (no turnover) ⇒ the whole symbol set — keeps the existing EB-0 run identical.
    assert fu.liquid_as_of(_panel(), t=4) == ["AAA", "BBB", "CCC", "DDD"]


def test_top_n_by_trailing_median_turnover() -> None:
    turn = {
        "AAA": [100.0] * 5,
        "BBB": [90.0] * 5,
        "CCC": [50.0] * 5,
        "DDD": [10.0] * 5,
    }
    assert fu.liquid_as_of(_panel(turn), t=4, top_n=2) == ["AAA", "BBB"]  # median desc


def test_delisted_name_excluded_at_t() -> None:
    turn = {"AAA": [100.0] * 5, "CCC": [50.0, 50.0, 50.0, 0.0, 0.0]}  # CCC delists after t=2
    assert fu.liquid_as_of(_panel(turn), t=4, top_n=5) == ["AAA"]  # CCC not trading at t=4


def test_not_yet_listed_excluded_at_t() -> None:
    turn = {"AAA": [100.0] * 5, "EEE": [0.0, 80.0, 80.0, 80.0, 80.0]}  # EEE lists at t=1
    assert fu.liquid_as_of(_panel(turn), t=0, top_n=5) == ["AAA"]  # EEE has no turnover yet
    assert set(fu.liquid_as_of(_panel(turn), t=4, top_n=5)) == {"AAA", "EEE"}  # entered by t=4


def test_excluded_symbol_dropped() -> None:
    turn = {"AAA": [100.0] * 5, "BBB": [90.0] * 5}  # dummy symbols — never real tickers
    fu.set_active(fu.Exclusions(symbols=frozenset({"AAA"}), source="dummy"))
    assert fu.liquid_as_of(_panel(turn), t=4, top_n=5) == ["BBB"]


def test_sub_floor_name_dropped_point_in_time() -> None:
    turn = {"AAA": [100.0] * 5, "CHEAP": [200.0] * 5}  # CHEAP is the more liquid name
    closes = {"AAA": [80.0] * 5, "CHEAP": [60.0, 60.0, 60.0, 40.0, 40.0]}  # dips below 50 at t=3
    fu.set_active(fu.Exclusions(price_floor_inr=50.0, source="dummy"))
    # At t=2 CHEAP (60 ≥ 50) ranks first by turnover; at t=4 it is sub-floor (40 < 50) and dropped.
    assert fu.liquid_as_of(_panel(turn, closes), t=2, top_n=5) == ["CHEAP", "AAA"]
    assert fu.liquid_as_of(_panel(turn, closes), t=4, top_n=5) == ["AAA"]


def test_fallback_respects_excluded_symbols() -> None:
    fu.set_active(fu.Exclusions(symbols=frozenset({"CCC"}), source="dummy"))
    assert fu.liquid_as_of(_panel(), t=4) == ["AAA", "BBB", "DDD"]  # full set minus excluded CCC
