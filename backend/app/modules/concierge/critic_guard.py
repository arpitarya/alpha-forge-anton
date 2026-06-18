"""Runtime money/PII critic — guard the one riskiest live write (`append_memory`).

The runtime twin of the `plan-store` constitutional rule: that rule blocks money/PII at
**commit** time; this blocks the same hard-identifier classes at the **runtime** write
boundary, before Orff's free text reaches the elgar store. Two layers, mirroring fux's
deterministic/judgment split (`runtime-note-pii` principle):

1. **Deterministic (block, $0, no LLM)** — the same PAN / Aadhaar / account-number patterns
   the commit-time `sentinel/pii_scanner` BLOCKs. A match refuses the write.
2. **Judgment (advisory, at first)** — `fux critic` surfaces money/PII judgment principles for
   host-agent self-critique. Advisory-first (fux ≥ 0.5.0): logged, not blocked, until escalated.
   Cage meters any tokens at the LLM gateway.

Scoped to `append_memory` only — do not widen until proven (see the `runtime-note-pii` rule).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field

from app.modules.concierge import fux_bridge

logger = logging.getLogger(__name__)

# Hard identifiers — mirror sentinel/pii_scanner BLOCK tier so runtime == commit-time.
_BLOCK_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("pan", re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")),
    ("aadhaar", re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b")),
    ("account-id",
     re.compile(r"(?i)\b(account|a/c|acct|client[_ -]?(id|code)|folio)\b\W{0,8}\d{6,}")),
]


class ForbiddenRuntimeActionError(Exception):
    """A deterministic money/PII invariant refused a runtime write. Never reaches the store."""

    def __init__(self, kind: str, detail: str) -> None:
        self.kind = kind
        super().__init__(detail)


@dataclass
class CriticVerdict:
    blocked: bool
    block_reason: str = ""
    suggestions: list[str] = field(default_factory=list)  # advisory judgment concerns


def _deterministic_block(note: str) -> tuple[str, str] | None:
    """First hard-identifier match → (kind, detail), else None. $0, in-process."""
    for kind, pat in _BLOCK_PATTERNS:
        if pat.search(note or ""):
            return kind, (f"hard identifier ({kind}) detected — money/PII never enters the "
                          "elgar store from a runtime note; remove it or use the operator path")
    return None


async def review_note(note: str) -> CriticVerdict:
    """Critique a proposed `orff-context` note BEFORE it is persisted.

    Deterministic PAN/Aadhaar/account match → blocked verdict (caller refuses the write).
    Otherwise run `fux critic` for the advisory judgment layer (best-effort, never blocks).
    """
    hit = _deterministic_block(note)
    if hit:
        kind, detail = hit
        logger.warning("critic_guard: deterministic block on runtime note (%s)", kind)
        return CriticVerdict(blocked=True, block_reason=detail)

    suggestions = await fux_bridge.critic_suggestions(note)  # advisory-first; "" on any failure
    return CriticVerdict(blocked=False, suggestions=suggestions)


async def guard_note(note: str) -> CriticVerdict:
    """Enforce: raise `ForbiddenRuntimeActionError` on a deterministic block, else return verdict.

    The single call site (`append_memory`) uses this — deterministic refusal is non-negotiable,
    advisory suggestions ride back on the verdict for the caller to log/surface.
    """
    verdict = await review_note(note)
    if verdict.blocked:
        raise ForbiddenRuntimeActionError("money/PII", verdict.block_reason)
    return verdict
