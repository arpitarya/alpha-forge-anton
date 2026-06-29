"""Flow Watch probe — deterministic decay detection + the decay-kill (elgar write mocked, no CDP).

Asserts: a healthy series stays HEALTHY (no kill); a series with negative expectancy / a -20%
drawdown / a losing streak DECAYS and recommends a kill with severity-tagged signals; the
decay-kill PII-guards its reason before journaling to elgar and NEVER mutates the frozen spec; and
Watch unlocks only for a surviving (passing) edge. Deterministic, $0, no LLM, no broker.

Run:  just probe flow-watch
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'OK' if ok else 'XX'} {name}{('  -- ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


async def main() -> int:
    from app.modules.edges.edge_journal import JournalRecord
    from app.modules.edges.edge_schema import EdgeSpec
    from app.modules.flow import flow_watch
    from app.modules.flow.flow_schema import StageId, StageState
    from app.modules.flow.flow_stages import derive
    from app.modules.flow.flow_watch_schema import DecaySeverity, Observation, WatchVerdict

    def obs(rs: list[float]):
        return [Observation(period=f"w{i}", return_pct=r) for i, r in enumerate(rs)]

    healthy = flow_watch.analyze(obs([3, 2, 4, 1]), expected=2.0)
    check("healthy series -> no kill", healthy.verdict == WatchVerdict.HEALTHY and not healthy.kill_recommended)

    decayed = flow_watch.analyze(obs([-3, -4, -5, -2, -6]), expected=2.0)
    check("decayed series -> kill recommended", decayed.verdict == WatchVerdict.DECAYED and decayed.kill_recommended)
    check("decay max-dd computed (-20%)", decayed.max_dd == -20.0)
    highs = {s.name for s in decayed.signals if s.severity == DecaySeverity.HIGH}
    check("severity-tagged HIGH signals",
          {"expectancy negative", "drawdown breach", "losing streak"} <= highs, str(highs))

    # decay-kill: PII guard then journal (elgar mocked)
    async def _save(*a, **k) -> str:
        return "elgar://plan/edge-x-retired"

    flow_watch.elgar_bridge.save = _save  # type: ignore[assignment]
    try:
        await flow_watch.retire("edge-x", "PAN ABCDE1234F", decayed)
        check("decay-kill PII guard blocks a PAN reason", False, "no error")
    except flow_watch.DecayKillError:
        check("decay-kill PII guard blocks a PAN reason", True)
    rec = await flow_watch.retire("edge-x", "expectancy collapsed", decayed)
    check("clean decay-kill journals a retirement", bool(rec.ref) and rec.max_dd == -20.0)

    # off-broker, no spec mutation: the Watch engine touches no broker or edge_store
    imports = [ln for ln in Path(flow_watch.__file__).read_text().splitlines()
               if ln.startswith(("import ", "from "))]
    check("Watch imports no broker / edge_store (frozen spec untouched)",
          not any(b in "\n".join(imports) for b in ("broker", "edge_store")))

    spec = EdgeSpec(id="e", hypothesis="h", signal="momentum")
    pas = JournalRecord(edge_id="e", run_at="2026-06-27T00:00:00Z", gate_reached=3, passed=True)
    kill = JournalRecord(edge_id="e", run_at="2026-06-27T00:00:00Z", gate_reached=0, passed=False)
    check("Watch ACTIVE on pass, BLOCKED on kill",
          {s.id: s for s in derive(spec, pas)}[StageId.WATCH].state == StageState.ACTIVE
          and {s.id: s for s in derive(spec, kill)}[StageId.WATCH].state == StageState.BLOCKED)

    print("\n" + ("XX flow-watch probe FAILED" if _fail else "OK Watch (decay monitor) guarantees hold"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
