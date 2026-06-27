"""Assemble the committed offline EB-0 panel from the raw NSE cache — offline, $0, deterministic.

Reads bars via `cache_read` (byte-integrity Gate-0: re-hash every cache file vs the manifest, refuse
corrupt bytes), builds the survivorship-safe liquidity superset (minus `--exclusions`),
densifies closes + turnover, runs per-rebalance Gate-0, writes a deterministic gzip panel. Panel
content depends only on the bytes NSE served, never fetch order or workers. See docs/edges.md.
"""

from __future__ import annotations

import argparse
from datetime import UTC, date, datetime
from pathlib import Path

from app.modules.edges import factor_universe as fu
from app.modules.edges.factor_panel import dump_panel
from app.modules.marketdata import cache_manifest as cm
from app.modules.marketdata.bhavcopy_manifest import Manifest, load_manifest, write_manifest
from app.modules.marketdata.cache_read import read_eq_bars, read_nifty
from app.modules.marketdata.panel_universe import align_turnover, gate0_per_week, liquid_superset
from app.modules.marketdata.panel_utils import align_closes

_OUT = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "marketdata"


def build(
    frm: str, to: str, top_n: int, out: Path, exclusions: fu.Exclusions | None = None
) -> dict:
    man = cm.load()
    bars, dates, rows = read_eq_bars(frm, to, man)  # verify-on-use: byte-integrity Gate-0
    if not dates:
        raise SystemExit(f"no cached sessions in [{frm}, {to}]; run just ingest-nse first")
    prev = fu.set_active(exclusions or fu.Exclusions())  # scope exclusions to this build
    try:
        universe = liquid_superset(bars, dates, top_n)  # excluded symbols never enter the superset
        panel = {
            "dates": dates,
            "closes": align_closes(bars, dates, universe),  # forward-filled (hold position value)
            "nifty": read_nifty(dates, man),
            "turnover": align_turnover(bars, dates, universe),  # 0 off-trading (no look-ahead)
        }
        gate0_per_week(panel, rows)  # Gate-0: eligible ⊆ that day's traders at every rebalance
    finally:
        fu.set_active(prev)
    out.mkdir(parents=True, exist_ok=True)
    dump_panel(panel, out / "panel.json.gz")  # deterministic gzip
    _finalize_manifest(out, frm, to, len(dates), len(universe))
    return panel


def _finalize_manifest(out: Path, frm: str, to: str, sessions: int, symbols: int) -> None:
    path = out / "manifest.json"
    m = load_manifest(path) if path.exists() else Manifest(
        fetched_at=datetime.now(UTC).isoformat(), from_date=frm, to_date=to
    )
    m.sessions, m.symbol_count = sessions, symbols
    write_manifest(m, path)


def main() -> int:
    p = argparse.ArgumentParser(description="Build the offline EB-0 panel from the NSE cache.")
    p.add_argument("--from", dest="frm", default="2016-01-01")
    p.add_argument("--to", dest="to", default=date.today().isoformat())
    p.add_argument("--top-n", type=int, default=250)
    p.add_argument("--out", type=Path, default=_OUT)
    p.add_argument("--exclusions", type=Path, default=None, help="elgar never-buy JSON (off-repo)")
    a = p.parse_args()
    excl = fu.load_exclusions(a.exclusions) if a.exclusions else fu.Exclusions()
    panel = build(a.frm, a.to, a.top_n, a.out, excl)
    print(f"OK panel: {len(panel['closes'])} symbols, {len(panel['dates'])} sessions -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
