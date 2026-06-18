"""Context-doc drift guard — fails if any standing-context elgar doc carries a
position figure (current holding quantity, comma-grouped portfolio ₹ value, or
signed P&L on a named holding).

These docs must stay figure-free; live holding data arrives via the
holdings-disclosure chokepoint (see `secure-holdings-plan` Fux entry).
Rule-level ₹ amounts (trade caps, SIP budgets, tax thresholds) are OK —
only per-holding state figures are forbidden.

When elgar is unreachable or a doc is absent, that check is skipped with a
warning — the probe never blocks CI on a missing store.

Standalone (no CDP). Run:  just probe context-drift
"""

from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

_fail = 0
_skipped = 0

# Position figures = per-holding current state data that goes stale.
# Rule-level ₹ amounts (₹2–3K caps, ₹20K SIP, ₹1.25L tax threshold) use K/L
# shorthand and are NOT matched here.
_POSITION_RX: dict[str, re.Pattern[str]] = {
    "holding qty (qty:/N shares/units)": re.compile(
        r"\bqty\s*[=:]\s*\d+|\b\d+\s+(?:shares?|units?)\b", re.I
    ),
    "signed P&L on a holding": re.compile(
        r"[Pp]&[Ll].*[+\-]\d|[+\-]\d+(?:\.\d+)?%.*[Pp]&[Ll]"
    ),
    "ltp / avg price field (stale price)": re.compile(
        r"\b(?:ltp|avg)\s+[\d,]+", re.I
    ),
    "comma-grouped INR value (portfolio ₹)": re.compile(
        r"(?:₹|Rs\.?|INR)\s*\d{1,3}(?:,\d{2,3})+"
    ),
    "now ₹ / current value ₹ (holding snapshot)": re.compile(
        r"\bnow\s+₹|\bcurrent\s+value\s+₹", re.I
    ),
}


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def scan_position_figures(text: str) -> list[tuple[int, str, str]]:
    hits: list[tuple[int, str, str]] = []
    for n, line in enumerate(text.splitlines(), 1):
        for label, rx in _POSITION_RX.items():
            if rx.search(line):
                hits.append((n, label, line.strip()[:80]))
    return hits


async def _check_all_docs(docs: tuple[str, ...]) -> None:
    global _skipped
    from app.modules.plans import elgar_bridge

    for doc_id in docs:
        try:
            text = await elgar_bridge.get(doc_id)
        except Exception as exc:
            print(f"⚠  {doc_id}  — elgar unavailable ({type(exc).__name__}), skipping")
            _skipped += 1
            continue

        if text is None:
            print(f"⚠  {doc_id}  — not in store yet, skipping")
            _skipped += 1
            continue

        hits = scan_position_figures(text)
        if hits:
            for line_no, label, snippet in hits:
                check(f"{doc_id}:{line_no}  [{label}]", False, snippet)
        else:
            check(f"{doc_id}  no position figures", True)


def main() -> int:
    from app.modules.concierge.memory_service import MEMORY_DOCS

    # Confirm the guard fires on a synthetic holding row (must precede live scans)
    synthetic = "RELIANCE · qty 50 @ avg 2,410, ltp 2,891 → now ₹1,44,550, P&L +19.9%"
    armed = scan_position_figures(synthetic)
    check("position-figure guard is armed", bool(armed),
          "patterns returned no hits — guard is broken")

    # Confirm rule-level ₹ amounts are NOT caught (avoid false positives)
    rule_text = "max ₹2–3K per trade; SIP ₹20K/month; LTCG above ₹1.25 lakh threshold"
    rule_hits = scan_position_figures(rule_text)
    check("rule-level ₹ amounts are NOT flagged", not rule_hits,
          f"false positives: {rule_hits}")

    asyncio.run(_check_all_docs(MEMORY_DOCS))

    suffix = f" ({_skipped} doc(s) not in store — skipped)" if _skipped else ""
    verdict = "❌ context-drift probe FAILED" if _fail else \
              f"✅ standing-context docs carry no position figures{suffix}"
    print(f"\n{verdict}")
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
