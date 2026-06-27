"""Gate-0 — a clean point-in-time universe passes; a seeded leak is rejected."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.modules.marketdata.bhavcopy_ingest import parse_bhavcopy
from app.modules.marketdata.bhavcopy_schema import UniverseSnapshot
from app.modules.marketdata.gate0_integrity import Gate0Error, assert_no_leak, check_leak

_FIX = Path(__file__).parent / "fixtures" / "bhavcopy"


def _rows():
    return parse_bhavcopy(_FIX / "2024-01-02.csv") + parse_bhavcopy(_FIX / "2024-01-03.csv")


def test_clean_universe_passes() -> None:
    clean = UniverseSnapshot(as_of="2024-01-02", symbols=["DELISTACME", "RELIANCE", "TCS"])
    assert check_leak(clean, _rows()) == ([], [])
    assert_no_leak(clean, _rows())  # does not raise


def test_seeded_leak_is_rejected() -> None:
    # A "currently-listed" universe applied to a past as_of: includes NEWCO (not yet
    # trading → look-ahead) and drops DELISTACME (was trading → survivorship).
    leaked = UniverseSnapshot(as_of="2024-01-02", symbols=["RELIANCE", "TCS", "NEWCO"])
    look_ahead, survivorship = check_leak(leaked, _rows())
    assert look_ahead == ["NEWCO"]
    assert survivorship == ["DELISTACME"]
    with pytest.raises(Gate0Error) as exc:
        assert_no_leak(leaked, _rows())
    assert "NEWCO" in str(exc.value) and "DELISTACME" in str(exc.value)
