"""Both NSE bhavcopy formats normalize identically; the index file yields the NIFTY close."""

from __future__ import annotations

from pathlib import Path

from app.modules.marketdata.bhavcopy_parse import parse_index_close, parse_raw

_FIX = Path(__file__).parent / "fixtures" / "bhavcopy_raw"
_DAY = "2024-01-02"


def _text(name: str) -> str:
    return (_FIX / name).read_text(encoding="utf-8")


def test_both_formats_parse_identically() -> None:
    udiff = parse_raw(_text("udiff_sample.csv"), _DAY)
    legacy = parse_raw(_text("cm_bhav_sample.csv"), _DAY)
    # The non-equity (series GB) row is dropped in BOTH formats.
    assert [r.symbol for r in udiff] == ["RELIANCE", "TCS"]
    # Same OHLC + ₹ turnover + ISIN + date regardless of the source format.
    assert udiff == legacy


def test_turnover_is_rupees_and_ohlc() -> None:
    rows = {r.symbol: r for r in parse_raw(_text("udiff_sample.csv"), _DAY)}
    assert rows["RELIANCE"].turnover == 3012000000.0  # ₹, not lakhs/crores
    assert rows["RELIANCE"].close == 2510.0
    assert rows["RELIANCE"].date == _DAY
    assert rows["RELIANCE"].isin == "INE002A01018"


def test_index_close_reads_named_index() -> None:
    txt = _text("ind_close_sample.csv")
    assert parse_index_close(txt) == 21741.90  # default Nifty 50
    assert parse_index_close(txt, "Nifty Bank") == 48150.75
    assert parse_index_close(txt, "Not An Index") is None
