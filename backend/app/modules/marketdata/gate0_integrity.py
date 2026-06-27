"""Gate-0 — the data-integrity admission test every universe must clear first.

A universe is honest only if it is exactly the set of symbols trading on the session at
its `as_of` — no more, no less. Against the full historical bhavcopy this catches the two
ways a universe leaks the future:

  • **look-ahead** — it contains a symbol not yet (or no longer) trading at `as_of`;
  • **survivorship** — it omits a symbol that *was* trading at `as_of` (typically a name
    that later delisted, silently dropped by a "currently-listed" universe builder).

`assert_no_leak` recomputes the canonical universe from the bars and rejects any mismatch,
so no backtest can ever read a universe that knows the future. Pure and deterministic.
"""

from __future__ import annotations

from app.modules.marketdata.bhavcopy_ingest import universe_as_of
from app.modules.marketdata.bhavcopy_schema import BhavRow, UniverseSnapshot


class Gate0Error(ValueError):
    """A universe failed the point-in-time / survivorship integrity gate."""


def check_leak(universe: UniverseSnapshot, rows: list[BhavRow]) -> tuple[list[str], list[str]]:
    """Return (look_ahead, survivorship) symbol lists — both empty ⇒ the universe is clean."""
    canonical = set(universe_as_of(rows, universe.as_of).symbols)
    provided = set(universe.symbols)
    look_ahead = sorted(provided - canonical)
    survivorship = sorted(canonical - provided)
    return look_ahead, survivorship


def assert_no_leak(universe: UniverseSnapshot, rows: list[BhavRow]) -> None:
    """Raise `Gate0Error` if the universe is not exactly the as-of session's symbols."""
    look_ahead, survivorship = check_leak(universe, rows)
    if look_ahead or survivorship:
        parts = []
        if look_ahead:
            parts.append(f"look-ahead (not trading at {universe.as_of}): {look_ahead}")
        if survivorship:
            parts.append(f"survivorship (dropped, was trading at {universe.as_of}): {survivorship}")
        raise Gate0Error("; ".join(parts))
