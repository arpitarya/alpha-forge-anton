"""The funnel — deterministic TestReport + signature, and pre-registration is enforced."""

from __future__ import annotations

import asyncio
import math
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.modules.edges.edge_register import PreRegistrationError
from app.modules.edges.edge_schema import EdgeSpec
from app.modules.edges.factor_panel import Panel
from app.modules.edges.factor_quality import FixtureFundamentals
from app.modules.edges.factor_schema import headline
from app.modules.edges.funnel import run_funnel

_PRE = datetime(2026, 6, 23, tzinfo=UTC)
_RUN = datetime(2026, 7, 1, tzinfo=UTC)


def _panel(n_days: int = 420, n_syms: int = 25) -> Panel:
    dates = [
        f"{2020 + i // 336:04d}-{(i // 28) % 12 + 1:02d}-{i % 28 + 1:02d}" for i in range(n_days)
    ]
    nifty = [
        1000.0 * (1.0008**i) for i in range(n_days)
    ]  # rising → above its 200-DMA after ~day 200
    closes = {
        f"S{k:02d}": [
            100.0 * ((1.0004 + 3e-5 * k) ** i) * (1 + 0.05 * math.sin(i / 9.0 + k))
            for i in range(n_days)
        ]
        for k in range(n_syms)
    }
    return Panel(dates=dates, closes=closes, nifty=nifty)


def _fund(n_syms: int = 25) -> FixtureFundamentals:
    syms = [f"S{k:02d}" for k in range(n_syms)]
    return FixtureFundamentals(dict.fromkeys(syms, 20.0), dict.fromkeys(syms, 0.3))


def _spec() -> EdgeSpec:
    return EdgeSpec(
        id="edge-001",
        hypothesis="cross-sectional momentum",
        universe=[],
        signal="momentum",
        holding_period_days=5,
        pre_registered_at=_PRE,
        factor=headline(),
    )


def _run(tmp: Path, run_at: datetime = _RUN):
    return asyncio.run(
        run_funnel(
            _spec(),
            _panel(),
            _fund(),
            seed=0,
            ledger_path=tmp / "trials.jsonl",
            run_at=run_at,
            pbo_partitions=6,
            mc_sims=40,
        )
    )


def test_report_and_signature_are_deterministic(tmp_path: Path) -> None:
    a = _run(tmp_path)
    b = _run(tmp_path)
    assert a.report.model_dump_json() == b.report.model_dump_json()
    assert a.signature == b.signature  # same panel + seed ⇒ byte-identical signed report
    assert a.report.edge_id == "edge-001"
    assert a.report.verdict in ("pass", "fail")  # an honest fail is an acceptable EB-0 outcome


def test_pre_registration_is_enforced(tmp_path: Path) -> None:
    with pytest.raises(PreRegistrationError):
        _run(tmp_path, run_at=_PRE - timedelta(days=1))  # run BEFORE the hypothesis was registered
