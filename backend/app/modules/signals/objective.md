---
monthly_target_inr: 0    # ← live value lives in the elgar copy only (never commit ₹ figures)
horizon: swing            # swing | long_term
risk_tolerance: aggressive  # conservative | moderate | aggressive
mission: ""               # free-text "why" — set in the elgar copy
# step_up:               # uncomment in elgar to schedule a raise; never commit ₹ values
#   from_date: 2026-07-01
#   monthly_target_inr: 0
---

# Objective config — north-star for Orff (knobs/labels only — no ₹ in this file)

Knobs only, git-safe. The live, operator-editable copy lives in the elgar `strategy/`
collection and overrides this file when present (`objective_config.load_objective`).
`set_objective` (Phase 2 mutating tool) writes changes there through the approval flow —
one elgar git commit, never a silent write.

| Knob | Meaning |
|------|---------|
| `monthly_target_inr` | Monthly realized-P&L target in INR — `0` means no target set |
| `step_up` | Optional scheduled raise — activates on/after `from_date` (`>=` semantics) |
| `horizon` | `swing` (days–weeks) or `long_term` (months–years) |
| `risk_tolerance` | Governs how Orff frames trade-offs in advice |
| `mission` | Free-text "why" — the goal this terminal serves (e.g. fund a recurring cost) |

`progress_pct` is a derived field on `RealizedReport` (`net / target * 100`, raw and
allowed-negative — a losing month reads negative; display clamping is frontend-only).
