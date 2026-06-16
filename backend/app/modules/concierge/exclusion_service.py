"""Add/remove a stock symbol from the hard-exclusion-list in elgar.

The list is a plain-text doc (one NSE ticker per line). Every write is via the
elgar CLI (same as save_memory) so each change is a git commit = audit trail.
Called ONLY from POST /concierge/exclusion after the user approves the ApprovalCard.
"""
from __future__ import annotations

from app.modules.plans import elgar_bridge

_DOC_ID = "hard-exclusion-list"


async def apply(symbol: str, action: str) -> str:
    """Add or remove `symbol` (normalised to uppercase); returns the updated list text."""
    if action not in ("add", "remove"):
        raise ValueError(f"action must be 'add' or 'remove', got {action!r}")
    sym = symbol.strip().upper()
    current = (await elgar_bridge.get(_DOC_ID) or "").strip()
    lines = [ln.strip() for ln in current.splitlines() if ln.strip()]
    if action == "add":
        if sym not in lines:
            lines.append(sym)
    else:
        lines = [ln for ln in lines if ln != sym]
    content = "\n".join(lines)
    await elgar_bridge.save(_DOC_ID, content, message=f"orff: {action} {sym} exclusion-list")
    return content
