"""Edge-discovery engine — pre-registered hypotheses through deterministic gates.

A separate concern from `signals.backtest` (which replays the *active* strategy
config). This is the discovery loop: a pre-registered `EdgeSpec` → gate 1 (out-of-
sample backtest) → gate 2 (walk-forward) → journal. No LLM computes any number.
The edge doc lives in the elgar store (`elgar://edge/<id>`), never in this repo.
"""
