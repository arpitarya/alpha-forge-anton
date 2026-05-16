"""Test suite for broker source plugins + portfolio routes.

Run from the backend directory:

    uv run pytest tests/test_brokers.py -v
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.brokers import (
    SOURCES,
    AssetClass,
    HoldingsAggregator,
    SourceKind,
    get_source,
)
from app.modules.brokers.broker_schemas import Holding
from app.modules.brokers.treemap_helper import squarify as _squarify


@pytest.fixture(autouse=True)
def reset_sources():
    """Clear cached holdings between tests."""
    for s in SOURCES.values():
        s.reset()
    yield
    for s in SOURCES.values():
        s.reset()


def _make_holding(**kwargs) -> Holding:
    defaults = dict(
        source="zerodha", asset_class=AssetClass.EQUITY, symbol="TEST",
        quantity=10.0, avg_price=100.0, last_price=110.0,
        invested=1000.0, current_value=1100.0, pnl=100.0, pnl_pct=10.0,
        exchange="NSE", as_of=datetime.now(UTC),
    )
    return Holding(**(defaults | kwargs))


def _seed_zerodha() -> HoldingsAggregator:
    """Inject five synthetic holdings directly into the zerodha source cache."""
    src = get_source("zerodha")
    holdings = [
        _make_holding(symbol="RELIANCE", quantity=120, avg_price=2410.0, last_price=2914.05,
                      invested=289200.0, current_value=349686.0, pnl=60486.0, pnl_pct=20.91,
                      isin="INE002A01018"),
        _make_holding(symbol="HDFCBANK", quantity=50, avg_price=1600.0, last_price=1520.0,
                      invested=80000.0, current_value=76000.0, pnl=-4000.0, pnl_pct=-5.0,
                      isin="INE040A01034"),
        _make_holding(symbol="INFY", quantity=30, avg_price=1500.0, last_price=1750.0,
                      invested=45000.0, current_value=52500.0, pnl=7500.0, pnl_pct=16.67,
                      isin="INE009A01021"),
        _make_holding(symbol="TCS", quantity=10, avg_price=3500.0, last_price=3800.0,
                      invested=35000.0, current_value=38000.0, pnl=3000.0, pnl_pct=8.57,
                      isin="INE467B01029"),
        _make_holding(symbol="WIPRO", quantity=100, avg_price=400.0, last_price=420.0,
                      invested=40000.0, current_value=42000.0, pnl=2000.0, pnl_pct=5.0,
                      isin="INE075A01022"),
    ]
    src._cached = holdings
    src._last_synced_at = datetime.now(UTC)
    from app.modules.brokers.base import SourceStatus
    src._status = SourceStatus.READY
    return HoldingsAggregator()


# ── Aggregator tests ──────────────────────────────────────────────────────────


class TestAggregator:
    def test_totals(self):
        agg = _seed_zerodha()
        t = agg.totals()
        assert t["count"] == 5
        assert t["invested"] > 0
        assert t["current_value"] > 0

    def test_treemap_cells_fit_unit_box(self):
        agg = _seed_zerodha()
        cells = agg.treemap()
        for c in cells:
            assert 0 <= c.left_pct <= 100
            assert 0 <= c.top_pct <= 100
            assert c.left_pct + c.width_pct <= 100.001
            assert c.top_pct + c.height_pct <= 100.001

    def test_rebalance_flags_drift_above_threshold(self):
        agg = _seed_zerodha()
        _, suggestions = agg.rebalance()
        actions = " ".join(s.action.lower() for s in suggestions)
        assert "trim equity" in actions


def test_squarify_unit_box():
    rects = _squarify([0.5, 0.3, 0.2], 0, 0, 1, 1)
    assert len(rects) == 3
    for x, y, w, h in rects:
        assert 0 <= x and 0 <= y
        assert x + w <= 1.0001
        assert y + h <= 1.0001


# ── HTTP route tests ──────────────────────────────────────────────────────────


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def loaded_client(client):
    """Client with zerodha holdings pre-seeded in memory."""
    _seed_zerodha()
    return client


class TestPortfolioRoutes:
    def test_list_sources(self, client):
        r = client.get("/api/v1/portfolio/sources")
        assert r.status_code == 200
        slugs = {s["slug"] for s in r.json()["sources"]}
        assert "zerodha" in slugs

    def test_holdings_no_filter_returns_all(self, loaded_client):
        r = loaded_client.get("/api/v1/portfolio/holdings")
        assert r.status_code == 200
        body = r.json()
        assert body["totals"]["count"] == 5
        assert "allocation" in body
        assert "disclaimer" in body

    def test_holdings_seeded_data_persists(self, client):
        _seed_zerodha()
        r = client.get("/api/v1/portfolio/holdings?source=zerodha")
        assert r.status_code == 200
        assert r.json()["totals"]["count"] == 5

        r2 = client.get("/api/v1/portfolio/holdings?source=zerodha")
        assert r2.status_code == 200
        assert r2.json()["totals"]["count"] == 5

    def test_holdings_unknown_source_returns_404(self, client):
        r = client.get("/api/v1/portfolio/holdings?source=unknown_broker")
        assert r.status_code == 404

    def test_treemap_returns_cells(self, loaded_client):
        r = loaded_client.get("/api/v1/portfolio/treemap")
        assert r.status_code == 200
        body = r.json()
        assert len(body["cells"]) == 5
        assert "disclaimer" in body

    def test_treemap_with_source_filter(self, loaded_client):
        r = loaded_client.get("/api/v1/portfolio/treemap?source=zerodha")
        assert r.status_code == 200
        assert len(r.json()["cells"]) == 5

    def test_treemap_unknown_source_returns_404(self, client):
        r = client.get("/api/v1/portfolio/treemap?source=unknown_broker")
        assert r.status_code == 404

    def test_rebalance_endpoint(self, client):
        r = client.get("/api/v1/portfolio/rebalance")
        assert r.status_code == 200
        body = r.json()
        assert "drift" in body and "suggestions" in body and "targets" in body

    def test_rebalance_with_data_has_equity_target(self, loaded_client):
        r = loaded_client.get("/api/v1/portfolio/rebalance")
        assert r.status_code == 200
        targets = r.json()["targets"]
        assert "equity" in targets


class TestSourceRoutes:
    def test_get_source_info(self, client):
        r = client.get("/api/v1/portfolio/sources/zerodha")
        assert r.status_code == 200
        body = r.json()
        assert body["slug"] == "zerodha"
        assert "kind" in body and "status" in body

    def test_get_unknown_source_returns_404(self, client):
        r = client.get("/api/v1/portfolio/sources/nonexistent")
        assert r.status_code == 404

    def test_sync_returns_valid_status(self, client):
        r = client.post("/api/v1/portfolio/sources/zerodha/sync")
        # API kind: either succeeds (200) or fails with auth error (400) — never 404
        assert r.status_code in (200, 400)


class TestSourceMetadata:
    def test_all_sources_are_api_kind(self):
        for slug, src in SOURCES.items():
            assert src.kind == SourceKind.API, f"{slug} should be API kind"
