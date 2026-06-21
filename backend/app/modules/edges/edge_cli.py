"""`just edge <id>` — load a pre-registered edge from elgar and run the discovery loop.

Thin CLI: read the `EdgeSpec` from the elgar `edges` collection, run gate 1 → gate 2,
print each gate's verdict + the journal outcome. Reports, it does not gate — always
exits 0 (a KILL is a successful run that killed a bad edge). If the spec is missing,
it says so and exits 0: the store is the source of truth, the repo holds no edge doc.

    just edge edge-20260621-...   |   uv run python -m app.modules.edges.edge_cli <id>
"""

from __future__ import annotations

import asyncio
import sys

from app.modules.edges.edge_discover import discover
from app.modules.edges.edge_schema import GateResult
from app.modules.edges.edge_store import load


def render(edge_id: str, gates: list[GateResult]) -> str:
    lines = [f"\n── Edge discovery: {edge_id}"]
    for g in gates:
        s = g.stats
        mark = "✅ PASS" if g.passed else "❌ KILL"
        lines.append(
            f"  gate {g.gate}  {mark}  trades {s.trades}  exp {s.expectancy_pct:+.3f}%  "
            f"hit {s.hit_rate:.0%}  Calmar {s.calmar}  maxDD {s.max_dd_pct:.2f}%"
        )
        lines += [f"    note: {n}" for n in g.notes]
    passed = bool(gates) and all(g.passed for g in gates)
    reached = max((g.gate for g in gates if g.passed), default=0)
    verdict = f"✅ cleared gates 1-{reached}" if passed else f"❌ killed at gate {reached + 1}"
    return "\n".join(lines) + f"\n\n{verdict}"


async def _amain(edge_id: str) -> int:
    spec = await load(edge_id)
    if spec is None:
        print(f"no edge {edge_id!r} in the elgar store — register it first (elgar://edge/<id>)")
        return 0
    print(render(edge_id, await discover(spec)))
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: edge_cli <edge-id>")
        return 0
    return asyncio.run(_amain(sys.argv[1]))


if __name__ == "__main__":
    raise SystemExit(main())
