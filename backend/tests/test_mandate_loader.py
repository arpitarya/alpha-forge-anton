"""Mandate loader — opex filled from the registry, covered honest-pending, fail-loud.

The personal ₹ figures live only in the elgar store; here we point the loader at a
tmp store so the test carries no real book values. Asserts the runtime fills
(`opex_per_month` from the funding registry, `covered=None`) and that a bad store path
RAISES rather than silently returning a default (`configurable-paths` fail-loud).

    uv run pytest tests/test_mandate_loader.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.modules.goals import mandate_loader

_MANDATE = {
    "aim": "Grow my capital as fast as it safely can — and prove it",
    "calmar_target": 3.0,
    "calmar_floor": 2.0,
    "drawdown_guard": {"soft": -12.0, "hard": -20.0},
    "horizon": "long_term",
    "risk_tolerance": "aggressive",
    "self_funding": {"opex_per_month": 0.0, "covered": True, "reserve": 16250.0},
    "capital_structure": {"groww": 87750.0, "zerodha": 87750.0, "reserve": 16250.0},
}


def _store(tmp_path: Path, payload: dict) -> Path:
    (tmp_path / "plans").mkdir(parents=True)
    (tmp_path / "plans" / "mandate.json").write_text(json.dumps(payload))
    return tmp_path


def test_loads_targets_and_structure(tmp_path, monkeypatch):
    monkeypatch.setattr(mandate_loader, "store_root", lambda: _store(tmp_path, _MANDATE))
    monkeypatch.setattr(mandate_loader, "opex_per_month", lambda: 4200.0)
    obj = mandate_loader.load_mandate()
    assert obj.calmar_target == 3.0 and obj.calmar_floor == 2.0
    assert obj.drawdown_guard.soft == -12.0 and obj.drawdown_guard.hard == -20.0
    assert obj.capital_structure.reserve == 16250.0


def test_opex_filled_from_registry_and_covered_honest_pending(tmp_path, monkeypatch):
    monkeypatch.setattr(mandate_loader, "store_root", lambda: _store(tmp_path, _MANDATE))
    monkeypatch.setattr(mandate_loader, "opex_per_month", lambda: 4200.0)
    obj = mandate_loader.load_mandate()
    assert obj.self_funding.opex_per_month == 4200.0  # registry, not the file's 0.0
    assert obj.self_funding.covered is None  # forced None even though file said True


def test_missing_store_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(mandate_loader, "store_root", lambda: tmp_path / "absent")
    with pytest.raises(FileNotFoundError):
        mandate_loader.load_mandate()
