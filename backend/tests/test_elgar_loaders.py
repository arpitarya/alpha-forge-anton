"""Loaders read elgar through the API (`elgar_bridge`), with seed/defaults fallback.

Anton owns no elgar store path (ADR `anton-delegates-elgar-store`); these assert the
read chain — elgar API → repo seed → typed defaults — and the cached-read invalidation,
all with a stubbed bridge so the suite stays offline (no store, no subprocess).

    uv run pytest tests/test_elgar_loaders.py -v
"""

from __future__ import annotations

import pytest

from app.modules.plans import elgar_bridge
from app.modules.signals import config_loader, objective_loader

_OBJ_DOC = "---\nmonthly_target_inr: 999.0\nrisk_tolerance: moderate\n---\n# Objective\n"


def test_objective_reads_from_elgar_api(monkeypatch):
    monkeypatch.setattr(elgar_bridge, "get_sync", lambda *a, **k: _OBJ_DOC)
    obj = objective_loader.load_objective()
    assert obj.monthly_target_inr == 999.0
    assert obj.risk_tolerance == "moderate"


def test_objective_falls_back_when_store_empty(monkeypatch):
    monkeypatch.setattr(elgar_bridge, "get_sync", lambda *a, **k: None)
    monkeypatch.setattr(objective_loader, "_seed", lambda: __import__("pathlib").Path("/no/such"))
    assert objective_loader.load_objective().monthly_target_inr == 0.0  # typed defaults


def test_config_reads_collection_strategy(monkeypatch):
    seen: dict = {}

    def _spy(doc_id, collection=None):
        seen["id"], seen["collection"] = doc_id, collection
        return None

    monkeypatch.setattr(elgar_bridge, "get_sync", _spy)
    monkeypatch.setattr(config_loader, "_seed", lambda: __import__("pathlib").Path("/no/such"))
    config_loader.load_config()
    assert seen == {"id": "strategy.config", "collection": "strategy"}


@pytest.mark.asyncio
async def test_save_invalidates_read_cache(monkeypatch):
    elgar_bridge._read_cache[("objective", "strategy")] = "stale"

    async def _ok(*a, **k):
        return (0, "")

    monkeypatch.setattr(elgar_bridge, "_run", _ok)
    await elgar_bridge.save("objective", "new", collection="strategy")
    assert ("objective", "strategy") not in elgar_bridge._read_cache
