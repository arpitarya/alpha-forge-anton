"""Bhavcopy ingest — parsing (incl. raw NSE header aliases), point-in-time universe, cache."""

from __future__ import annotations

from pathlib import Path

from app.modules.marketdata.bhavcopy_ingest import (
    parse_bhavcopy,
    universe_as_of,
    write_bhavcopy,
)

_FIX = Path(__file__).parent / "fixtures" / "bhavcopy"


def test_parse_skips_comment_and_reads_bars() -> None:
    rows = parse_bhavcopy(_FIX / "2024-01-02.csv")
    assert len(rows) == 3
    reliance = next(r for r in rows if r.symbol == "RELIANCE")
    assert reliance.close == 2510.0
    assert reliance.isin == "INE002A01018"
    assert reliance.date == "2024-01-02"


def test_parse_accepts_raw_nse_aliases(tmp_path: Path) -> None:
    raw = tmp_path / "raw.csv"
    raw.write_text(
        "SYMBOL,SERIES,OPEN_PRICE,HIGH_PRICE,LOW_PRICE,CLOSE_PRICE,TOTTRDQTY,ISIN\n"
        "INFY,EQ,1500,1520,1495,1510,900000,INE009A01021\n",
        encoding="utf-8",
    )
    rows = parse_bhavcopy(raw, day="2024-01-02")
    assert len(rows) == 1
    assert rows[0].symbol == "INFY" and rows[0].close == 1510.0
    assert rows[0].volume == 900000.0 and rows[0].date == "2024-01-02"


def test_universe_as_of_is_point_in_time() -> None:
    rows = parse_bhavcopy(_FIX / "2024-01-02.csv") + parse_bhavcopy(_FIX / "2024-01-03.csv")
    assert universe_as_of(rows, "2024-01-02").symbols == ["DELISTACME", "RELIANCE", "TCS"]
    assert universe_as_of(rows, "2024-01-03").symbols == ["NEWCO", "RELIANCE", "TCS"]
    # A date before any session yields an empty universe (no look-back invented).
    assert universe_as_of(rows, "2023-12-31").symbols == []


def test_cache_round_trip(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PORTFOLIO_DUMP_DIR", str(tmp_path))
    monkeypatch.setenv("NSE_DATA_DIR", str(tmp_path))  # bhavcopy cache dir
    rows = parse_bhavcopy(_FIX / "2024-01-02.csv")
    dst = write_bhavcopy(rows, "2024-01-02")
    assert dst.exists() and (dst.stat().st_mode & 0o777) == 0o600
    assert parse_bhavcopy(dst) == rows
