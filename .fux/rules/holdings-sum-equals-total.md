---
id: holdings-sum-equals-total
domain: portfolio
type: invariant
status: active
created: 2026-06-03
updated: 2026-06-03
code_refs:
  - backend/app/modules/brokers/aggregator.py#L38-L59
related: [portfolio-valuation, inr-normalization]
aliases: [conservation, sum equals total, roll-up integrity]
keywords: [invariant, total, holdings, sum, parity]
check: "abs(sum(inr_values) - current_value) < 0.01"
verify_cmd: "cd backend && uv run python ../probes/fux_totals_probe.py 2>/dev/null"
---
**Invariant:** The portfolio's `current_value` total **must equal** the sum of
its per-holding INR values: `Σ inr_value(h) == totals.current_value` (to ₹0.01).

**Why:** the total is a derived aggregate. If it ever diverges from the sum of
its parts, a holding was dropped, double-counted, or a currency wasn't normalised
([[inr-normalization]]). This is the one assertion that catches a whole class of
roll-up bugs cheaply.

**How it's checked:** `fux verify` runs `probes/fux_totals_probe.py` (the probe
emits `inr_values` + `current_value` as JSON) and evaluates `check:` against it.
No live session → caches empty → `0 == 0` holds; with data it validates parity.
