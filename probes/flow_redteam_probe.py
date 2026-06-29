"""Flow Red-team probe — the only LLM stage (mocked gateway: no spend, deterministic).

Asserts the service's guarantees without billing the LLM: it parses the model's JSON into a
severity-sorted `RedteamReport`, runs one repair round on bad JSON then succeeds, caches per
edge (no re-bill), and is OFF the deterministic path — `flow_redteam` never IMPORTS the
funnel/sizing engines (numbers in, never recomputed). The real call is cage-metered by the
gateway at runtime.

Run:  just probe flow-redteam
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

_fail = 0
_GOOD = (
    '{"objections": [{"severity": "low", "title": "costs"}, '
    '{"severity": "high", "title": "overfit"}], "tenth_man": "regime change", '
    '"runner_ups": ["wait for confirmation"], "tripwires": ["NIFTY < 200DMA"]}'
)


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


class _Resp:
    def __init__(self, content: str) -> None:
        self.content, self.provider, self.model = content, "claude-sdk", "claude-opus-4-8"


async def main() -> int:
    from app.modules.flow import flow_redteam
    from app.modules.flow.flow_redteam_schema import RedteamContext, Severity
    from app.modules.flow.flow_run_schema import RunPhase

    # 1. parse + severity sort (loudest first)
    r = flow_redteam._parse(_GOOD, "claude-sdk", "claude-opus-4-8")
    check("objections sorted high→low", [o.severity for o in r.objections] == [Severity.HIGH, Severity.LOW])
    check("10th-Man + tripwires parsed", r.tenth_man == "regime change" and r.tripwires == ["NIFTY < 200DMA"])
    check("provider recorded (metering attribution)", r.provider == "claude-sdk")

    # 2. one repair round recovers from bad JSON
    calls = {"n": 0}

    async def _complete(messages, **kw):
        calls["n"] += 1
        return _Resp("oops not json" if calls["n"] == 1 else _GOOD)

    flow_redteam._gateway.complete = _complete  # type: ignore[assignment]
    rep = await flow_redteam._complete(flow_redteam.build_messages(RedteamContext(edge_id="e")))
    check("repair round recovers (2 calls, then done)", calls["n"] == 2 and rep.phase == RunPhase.DONE)

    # 3. cache + no double-run
    flow_redteam._CACHE.clear()
    ctx = RedteamContext(edge_id="edge-x", verdict="pass")
    a = flow_redteam.start(ctx)
    check("first start → queued", a.phase == RunPhase.QUEUED)
    check("no double-run (same cached object)", flow_redteam.start(ctx) is flow_redteam.get("edge-x"))
    await asyncio.sleep(0.05)
    check("job completes + caches", flow_redteam.get("edge-x").phase == RunPhase.DONE)

    # 4. OFF the deterministic path — no funnel/sizing imports
    imports = [
        ln for ln in Path(flow_redteam.__file__).read_text().splitlines()
        if ln.startswith(("import ", "from "))
    ]
    joined = "\n".join(imports)
    check("red-team imports no funnel/sizing engine",
          "funnel" not in joined and "flow_sizing" not in joined and "factor_" not in joined)

    print("\n" + ("❌ flow-redteam probe FAILED" if _fail else "✅ Red-team (LLM) guarantees hold"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
