"""`just eb0-real` — run edge-001's frozen campaign against the REAL nse-bhavcopy panel.

The Phase-1b base-rate verdict: the same pinned 24-config grid + pre-registration, but on the
committed real panel (`data_provenance = nse-bhavcopy`) with the quality leg DISABLED-PENDING: there
is no point-in-time ROCE/D-E feed yet, so it runs momentum + trend only and counts every name as
unscreened (applying today's fundamentals to history would be look-ahead, which Gate-0 forbids). A
PASS and a KILL are both valid; nothing is tuned. The ₹/performance result is an edge result: it is
JOURNALED to elgar (edges-journal, `elgar://edge/<id>`), NEVER written into this repo. Offline/$0.
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import UTC, datetime
from pathlib import Path

from app.modules.edges import edge_journal
from app.modules.edges.eb0_cli import edge_001, render
from app.modules.edges.factor_panel import load_panel
from app.modules.edges.factor_quality import FixtureFundamentals
from app.modules.edges.factor_universe import Exclusions, load_exclusions
from app.modules.edges.funnel import FunnelResult, run_funnel

_REAL = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "marketdata" / "panel.json.gz"
_NO_FEED = FixtureFundamentals({}, {})  # no point-in-time fundamentals → every name honest-pending


async def run_real(
    panel_path: Path = _REAL,
    *,
    journal: bool = True,
    ledger_path: Path | None = None,
    exclusions: Exclusions | None = None,
) -> FunnelResult:
    if not panel_path.exists():
        raise SystemExit(
            f"no real panel at {panel_path} — run `just ingest-nse FROM TO` then `just build-panel`"
        )
    res = await run_funnel(
        edge_001(),
        load_panel(panel_path),
        _NO_FEED,
        seed=0,
        ledger_path=ledger_path,
        data_provenance="nse-bhavcopy",
        quality_on=False,
        exclusions=exclusions or Exclusions(),
    )
    if journal:  # best-effort — a down/absent store never blocks the run
        await edge_journal.append(edge_journal.from_report(res.report, datetime.now(UTC)))
    return res


def main() -> int:
    p = argparse.ArgumentParser(description="Run edge-001 on the real nse-bhavcopy panel.")
    p.add_argument("--exclusions", type=Path, default=None, help="elgar never-buy JSON (off-repo)")
    a = p.parse_args()
    excl = load_exclusions(a.exclusions) if a.exclusions else Exclusions()
    res = asyncio.run(run_real(exclusions=excl))
    print(render(res))
    print("\nResult JOURNALED to elgar (edges-journal) — figures are NOT committed to this repo.")
    print("PASS and honest KILL are both valid EB-0 outcomes — nothing here is tuned.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
