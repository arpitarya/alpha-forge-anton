"""Action confirmation — detect a mutating intent in the user's message and emit
a structured approval card instead of relying on prose "shall I proceed?".

Anton never places orders; approving a card sends an explicit confirmation turn
back into the conversation, so each step of a multi-step action is user-gated.
The card's steps are honest about that boundary."""

from __future__ import annotations

import re

_ACTIONS: list[tuple[re.Pattern[str], str, list[str]]] = [
    (
        re.compile(r"\brebalanc", re.IGNORECASE),
        "Rebalance portfolio",
        [
            "Compute drift vs the committed plan",
            "Draft buy/sell legs with sizes and rationale",
            "You review the legs and place orders at your broker",
        ],
    ),
    (
        re.compile(r"\b(buy|sell|exit|trim|add)\b.{0,40}\b(position|stock|share|holding|sleeve)",
                    re.IGNORECASE),
        "Adjust a position",
        [
            "Quantify the size and portfolio impact",
            "Check concentration ceilings and tax lots",
            "You confirm and execute at your broker",
        ],
    ),
    (
        re.compile(r"\b(sync|refresh|re-?fetch)\b.{0,30}\b(broker|holding|source)", re.IGNORECASE),
        "Refresh broker data",
        [
            "Trigger a sync of connected broker sources",
            "Recompute totals once fresh rows land",
        ],
    ),
    (
        re.compile(r"\b(deploy|invest|put)\b.{0,30}\b(cash|lakh|crore|₹|lump)", re.IGNORECASE),
        "Deploy cash",
        [
            "Stage tranches per the plan's allocation bands",
            "Surface entry checks (concentration, emergency fund)",
            "You confirm each tranche before placing it",
        ],
    ),
]


def detect_action(text: str) -> dict | None:
    """A structured pending-action card for a mutating intent, else None."""
    for pattern, label, steps in _ACTIONS:
        if pattern.search(text or ""):
            return {
                "id": re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-"),
                "action": label,
                "summary": text.strip()[:160],
                "steps": steps,
            }
    return None
