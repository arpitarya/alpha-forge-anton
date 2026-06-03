"""Fux invariant probe — emits the holdings-vs-total context as JSON.

Wires the `holdings-sum-equals-total` Fux invariant (.fux/rules/) into the probe
culture (see probes/WHY_PROBES_NOT_MCP.md). Prints, to stdout:

    {"inr_values": [...per-holding INR value...], "current_value": <totals current>}

`fux verify` evaluates the rule's `check:` against this. With no live broker
session the caches are empty (sum 0 == current 0 — the invariant holds trivially);
with real holdings it validates that the roll-up equals the sum of its parts.

Run:  cd backend && uv run python ../probes/fux_totals_probe.py
"""
from __future__ import annotations

import json
import sys


def main() -> int:
    try:
        from app.modules.brokers.aggregator import HoldingsAggregator, _inr_value
    except Exception as exc:  # noqa: BLE001 — no backend env → verify skips gracefully
        print(f"# fux probe: backend import unavailable ({exc})", file=sys.stderr)
        return 1
    agg = HoldingsAggregator()
    holdings = agg.all_holdings()
    payload = {
        "inr_values": [round(_inr_value(h), 2) for h in holdings],
        "current_value": agg.totals()["current_value"],
    }
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
