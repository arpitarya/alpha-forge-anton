"""EB-0 probe — the #1 proof runs end-to-end, deterministically, offline (no network, no LLM).

Asserts: (1) pre-registration is enforced (a post-hoc run is refused), (2) the signed TestReport is
byte-identical across two runs on the same panel + seed (reproducibility), and (3) the null-data
trust check still finds NO edge. The EB-0 verdict may be PASS or KILL — both honest; the probe
checks the machinery, never forces an outcome.

Run:  just probe eb0   |   uv run python probes/eb0_probe.py
"""

from __future__ import annotations

import asyncio
import sys
import tempfile
from datetime import timedelta
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "backend"))

from app.modules.edges.eb0_cli import EDGE_001_PRE, edge_001, fundamentals, render  # noqa: E402
from app.modules.edges.edge_register import PreRegistrationError  # noqa: E402
from app.modules.edges.factor_panel import load_panel  # noqa: E402
from app.modules.edges.funnel import run_funnel  # noqa: E402
from app.modules.edges.null_selftest import run_null_selftest  # noqa: E402

_PANEL = _ROOT / "backend" / "tests" / "fixtures" / "eb0" / "panel.json"
_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


async def _run() -> None:
    panel = load_panel(_PANEL)
    with tempfile.TemporaryDirectory() as d:
        led = Path(d) / "trials.jsonl"
        a = await run_funnel(edge_001(), panel, fundamentals(), seed=0, ledger_path=led)
        b = await run_funnel(edge_001(), panel, fundamentals(), seed=0, ledger_path=led)
    check(
        "TestReport byte-identical across runs",
        a.report.model_dump_json() == b.report.model_dump_json(),
    )
    check("signature identical across runs", a.signature == b.signature)
    check("verdict is a real pass/fail", a.report.verdict in ("pass", "fail"))

    refused = False
    try:
        await run_funnel(edge_001(), panel, fundamentals(), run_at=EDGE_001_PRE - timedelta(days=1))
    except PreRegistrationError:
        refused = True
    check("post-hoc run refused (pre-registration)", refused)
    check("null-data still finds NO edge", await run_null_selftest(25) == 0)
    print(render(a))


def main() -> int:
    asyncio.run(_run())
    print(
        "\n"
        + ("❌ EB-0 probe FAILED" if _fail else "✅ EB-0: deterministic, pre-registered, signed")
    )
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
