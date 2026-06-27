"""Quality overlay — keep on ROCE/D-E, and honest-pending when fundamentals are unknown."""

from __future__ import annotations

from app.modules.edges.factor_quality import FixtureFundamentals, quality_filter
from app.modules.edges.factor_schema import FactorConfig


def test_keeps_passing_and_pends_unknown() -> None:
    fund = FixtureFundamentals(
        roce={"A": 20.0, "B": 10.0, "C": 16.0},  # D omitted → unknown
        debt_equity={"A": 0.3, "B": 0.4, "C": 0.6},
    )
    kept, pending = quality_filter(["A", "B", "C", "D"], FactorConfig(), fund)
    assert kept == ["A"]  # B fails ROCE<15; C fails D/E>0.5
    assert pending == ["D"]  # unknown fundamentals → honest-pending, never faked into kept


def test_theta_de_loosening_admits_more() -> None:
    fund = FixtureFundamentals(roce={"C": 16.0}, debt_equity={"C": 0.8})
    assert quality_filter(["C"], FactorConfig(theta_de=0.5), fund) == ([], [])
    assert quality_filter(["C"], FactorConfig(theta_de=1.0), fund) == (["C"], [])
