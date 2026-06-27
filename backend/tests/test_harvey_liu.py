"""Harvey-Liu haircut — more tests means a bigger haircut and a lower surviving t-stat."""

from __future__ import annotations

from app.modules.edges.harvey_liu import haircut


def test_more_tests_means_more_haircut() -> None:
    sr, n_obs = 0.5, 260  # a strong-ish weekly Sharpe over ~5y
    t1, frac1 = haircut(sr, n_obs, 1)
    t24, frac24 = haircut(sr, n_obs, 24)
    assert frac24 > frac1 >= 0.0  # more tests → more of the Sharpe is haircut away
    assert t24 < t1  # the surviving adjusted t-stat shrinks


def test_no_edge_is_fully_haircut() -> None:
    assert haircut(0.0, 100, 24) == (0.0, 1.0)
    assert haircut(-0.2, 100, 24) == (0.0, 1.0)
