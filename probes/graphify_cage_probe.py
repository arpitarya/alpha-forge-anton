"""Graphify×cage metering probe — the wrapped query files a receipt; off-repo emits none.

Verifies Stage 2 of the cage data-wiring (docs/cage.md): the `bin/graphify` shim
routes a query through `cage graphify -- graphify …` so a `tool="graphify"`,
`method="modeled"` token-saving receipt lands in the ledger — while a query whose
cited source files don't resolve (off-repo / no graph) files **nothing** (an
unmeasurable saving is not a zero row). Standalone, no CDP. Prints JSON:

    {"in_repo_receipt": {...}, "off_repo_receipts": 0}

`fux verify` / the just recipe assert: in_repo_receipt.tool == "graphify",
method == "modeled", saved > 0; off_repo_receipts == 0.

Run:  just probe graphify-cage   (needs graphify CLI + the [cage] extra)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SHIM = _ROOT / "bin" / "graphify"


def _run(query: str, cwd: Path, ledger: Path) -> None:
    """Invoke the metering shim for one query against an isolated ledger (best-effort)."""
    env = {**os.environ, "CAGE_LEDGER": str(ledger)}
    subprocess.run(
        [str(_SHIM), "query", query], cwd=cwd, env=env, capture_output=True, text=True
    )


def _receipts(ledger: Path) -> list[dict]:
    f = ledger / "receipts.jsonl"
    if not f.exists():
        return []
    return [json.loads(line) for line in f.read_text().splitlines() if line.strip()]


def main() -> int:
    if not _SHIM.exists() or not (_ROOT / "graphify-out" / "graph.json").exists():
        print(
            "# graphify-cage probe: shim or graph missing — skipping", file=sys.stderr
        )
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        # In-repo query → cited source files resolve → one graphify receipt.
        in_ledger = Path(tmp) / "in"
        _run("how does the holdings aggregator relate to brokers", _ROOT, in_ledger)
        gf = [r for r in _receipts(in_ledger) if r.get("tool") == "graphify"]

        # Off-repo query (a dir with no graph) → graphify errors → nothing filed.
        off_dir = Path(tmp) / "offrepo"
        off_dir.mkdir()
        off_ledger = Path(tmp) / "off"
        _run("anything at all", off_dir, off_ledger)

        print(
            json.dumps(
                {
                    "in_repo_receipt": gf[0] if gf else None,
                    "off_repo_receipts": len(_receipts(off_ledger)),
                }
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
