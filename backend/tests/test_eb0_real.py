"""eb0_real_cli.run_real — real-provenance verdict with the quality leg disabled-pending.

Drives the real-run path on a synthetic-shaped panel that carries a turnover block (so the
per-rebalance liquidity universe engages). Asserts the TestReport is self-describing
(data_provenance, date range, quality unvalidated + pending counted, per-rebalance universe), the
run is deterministic, and a missing panel errors honestly. No real ₹ data, no network, no store.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from app.modules.edges.eb0_real_cli import run_real

_BASE = date(2020, 1, 1)


def _panel_dict(n: int = 420, k: int = 12) -> dict:  # ≥420 so the lookback-15 grid configs run
    dates = [(_BASE + timedelta(days=i)).isoformat() for i in range(n)]
    nifty = [1000.0 * (1.0008**i) for i in range(n)]  # rising → above its 200-DMA after ~day 200
    closes = {f"S{j:02d}": [100.0 * ((1.0005 + 1e-5 * j) ** i) for i in range(n)] for j in range(k)}
    turnover = {f"S{j:02d}": [1e7 * (k - j)] * n for j in range(k)}  # S00 most liquid
    return {"dates": dates, "closes": closes, "nifty": nifty, "turnover": turnover}


def _write(tmp_path: Path) -> Path:
    p = tmp_path / "panel.json"
    p.write_text(json.dumps(_panel_dict()), encoding="utf-8")
    return p


async def test_real_run_is_self_describing(tmp_path) -> None:
    r = (await run_real(_write(tmp_path), journal=False, ledger_path=tmp_path / "t.jsonl")).report
    assert r.data_provenance == "nse-bhavcopy"
    assert r.quality_status == "disabled-pending"
    assert r.quality_pending > 0  # momentum+trend names counted, never quality-faked
    assert r.universe_status == "per-rebalance-liquid"
    assert r.date_from == _panel_dict()["dates"][0]
    assert r.date_to == _panel_dict()["dates"][-1]
    assert r.verdict in ("pass", "fail")


async def test_real_run_is_deterministic(tmp_path) -> None:
    p, led = _write(tmp_path), tmp_path / "t.jsonl"
    a = await run_real(p, journal=False, ledger_path=led)
    b = await run_real(p, journal=False, ledger_path=led)
    assert a.signature == b.signature
    assert a.report.model_dump_json() == b.report.model_dump_json()


async def test_missing_panel_errors_honestly(tmp_path) -> None:
    with pytest.raises(SystemExit):
        await run_real(tmp_path / "nope.json", journal=False, ledger_path=tmp_path / "t.jsonl")
