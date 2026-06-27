"""Gate-0 data-integrity probe — bhavcopy loads, leak rejected, clean accepted (offline).

Standalone (no network, no store): loads the two-session bhavcopy fixture and asserts
  • the point-in-time universe at 2024-01-02 is exactly that session's symbols,
  • a "currently-listed" universe applied to the past is REJECTED (look-ahead + survivorship),
  • the honest point-in-time universe is ACCEPTED.

Run:  just probe gate0   |   uv run python probes/gate0_integrity_probe.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "backend"))

from app.modules.marketdata.bhavcopy_ingest import parse_bhavcopy, universe_as_of
from app.modules.marketdata.bhavcopy_schema import UniverseSnapshot
from app.modules.marketdata.gate0_integrity import Gate0Error, assert_no_leak

_FIX = _ROOT / "backend" / "tests" / "fixtures" / "bhavcopy"
_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def main() -> int:
    rows = parse_bhavcopy(_FIX / "2024-01-02.csv") + parse_bhavcopy(_FIX / "2024-01-03.csv")
    check("bhavcopy loads (2 sessions, 6 bars)", len(rows) == 6, f"got {len(rows)}")

    pit = universe_as_of(rows, "2024-01-02").symbols
    check("point-in-time universe is the as-of session", pit == ["DELISTACME", "RELIANCE", "TCS"], str(pit))

    leaked = UniverseSnapshot(as_of="2024-01-02", symbols=["RELIANCE", "TCS", "NEWCO"])
    rejected = False
    try:
        assert_no_leak(leaked, rows)
    except Gate0Error as e:
        rejected = True
        print(f"   ↳ Gate-0 rejected: {e}")
    check("seeded leak (look-ahead + survivorship) is REJECTED", rejected)

    clean = UniverseSnapshot(as_of="2024-01-02", symbols=pit)
    accepted = True
    try:
        assert_no_leak(clean, rows)
    except Gate0Error:
        accepted = False
    check("honest point-in-time universe is ACCEPTED", accepted)

    print("\n" + ("❌ Gate-0 FAILED" if _fail else "✅ Gate-0: no look-ahead, no survivorship"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
