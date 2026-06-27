"""Cross-sectional momentum — score, deterministic ranking, decile/quartile selection."""

from __future__ import annotations

import pytest

from app.modules.edges.factor_panel import Panel
from app.modules.edges.factor_rank import momentum_score, rank_desc, select
from app.modules.edges.factor_schema import FactorConfig


def _dates(n: int) -> list[str]:
    return [f"2024-{i // 28 % 12 + 1:02d}-{i % 28 + 1:02d}" for i in range(n)]


def _cfg() -> FactorConfig:
    return FactorConfig(lookback_months=1, skip_month=False)  # lookback 21d, no skip


def test_momentum_score_and_insufficient_history() -> None:
    closes = [100.0] * 21 + [110.0]
    assert momentum_score(closes, 21, 21, 0) == pytest.approx(0.1)
    assert momentum_score(closes, 10, 21, 0) is None  # not enough lookback


def test_rank_desc_and_select() -> None:
    n = 20
    closes = {f"S{k:02d}": [100.0] * 21 + [100.0 * (1 + k / 100)] for k in range(n)}
    panel = Panel(dates=_dates(22), closes=closes, nifty=[0.0] * 22)
    ranked = rank_desc(panel, 21, _cfg())
    assert ranked[:2] == ["S19", "S18"]  # highest momentum first, ties broken by symbol
    assert select(ranked, "decile") == ["S19", "S18"]  # 10% of 20 = 2
    assert len(select(ranked, "quartile")) == 5  # 25% of 20
    assert select([], "decile") == []
