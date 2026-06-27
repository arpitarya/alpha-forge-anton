"""EB-0 real-run probe — the nse-bhavcopy verdict path, offline (no network, no store, no LLM).

Runs `eb0_real_cli.run_real` on a synthetic-SHAPED panel that carries a turnover block (so the
per-rebalance liquidity universe engages — not real ₹ data). Asserts: the TestReport is tagged
`data_provenance=nse-bhavcopy` with the quality leg `disabled-pending` (pending counted, never
faked), the per-rebalance universe is active, the signed report is byte-identical across runs,
journaling is best-effort (no crash when the elgar store is absent), and null-data still finds NO
edge. PASS or KILL are both valid — the probe checks the machinery, never forces an outcome.

Run:  just probe eb0-real   |   uv run python probes/eb0_real_probe.py
"""

from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from datetime import date, timedelta
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "backend"))

from app.modules.edges.eb0_real_cli import run_real  # noqa: E402
from app.modules.edges.factor_universe import load_exclusions  # noqa: E402
from app.modules.edges.null_selftest import run_null_selftest  # noqa: E402

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def _panel(path: Path, n: int = 420, k: int = 12) -> None:
    base = date(2020, 1, 1)
    dates = [(base + timedelta(days=i)).isoformat() for i in range(n)]
    nifty = [1000.0 * (1.0008**i) for i in range(n)]  # rising → above its 200-DMA after ~day 200
    closes = {f"S{j:02d}": [100.0 * ((1.0005 + 1e-5 * j) ** i) for i in range(n)] for j in range(k)}
    turnover = {f"S{j:02d}": [1e7 * (k - j)] * n for j in range(k)}
    path.write_text(json.dumps({"dates": dates, "closes": closes, "nifty": nifty,
                                "turnover": turnover}), encoding="utf-8")


async def _run() -> None:
    with tempfile.TemporaryDirectory() as d:
        tmp = Path(d)
        panel, led = tmp / "panel.json", tmp / "trials.jsonl"
        _panel(panel)
        a = await run_real(panel, journal=False, ledger_path=led)
        b = await run_real(panel, journal=False, ledger_path=led)
        r = a.report
        check("data_provenance = nse-bhavcopy", r.data_provenance == "nse-bhavcopy")
        check("quality leg disabled-pending", r.quality_status == "disabled-pending")
        check("pending names counted (not faked)", r.quality_pending > 0, str(r.quality_pending))
        check("per-rebalance liquidity universe", r.universe_status == "per-rebalance-liquid")
        check("date range stamped", bool(r.date_from and r.date_to))
        check("verdict is a real pass/fail", r.verdict in ("pass", "fail"))
        check("signed report byte-identical across runs", a.signature == b.signature)
        # journaling is best-effort: an absent elgar store must not raise.
        await run_real(panel, journal=True, ledger_path=led)
        check("journaling best-effort (no crash when store absent)", True)
        # runtime exclusions surface as COUNT + source only (dummy symbols — never real tickers).
        epath = tmp / "excl.json"
        epath.write_text(json.dumps({"symbols": ["S00", "S01"], "price_floor_inr": 50}))
        e = await run_real(panel, journal=False, ledger_path=led, exclusions=load_exclusions(epath))
        check("exclusions count surfaced (no tickers)", e.report.exclusions_count == 2)
        check("exclusions source recorded", e.report.exclusions_source == "excl")
    check("null-data still finds NO edge", await run_null_selftest(25) == 0)


def main() -> int:
    asyncio.run(_run())
    ok = "✅ EB-0-real: nse-bhavcopy provenance, quality-pending, per-rebalance, signed"
    print("\n" + ("❌ EB-0-real probe FAILED" if _fail else ok))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
