"""Git-safety guard — the enforcement behind the two-plane rule.

A committed plan / drift doc belongs to the *plan plane*: strategy only (target %,
bands, rules). It must never carry *data-plane* figures — ₹ amounts, quantities,
account/client IDs, or broker secrets. This scans every plan-plane doc under
`.fux/rules/` and FAILS (exit 1) on the first leak, so "safe in a public repo" is a
guarantee, not a convention. See the `secure-holdings-plan` Fux entry.

Standalone — no backend, no CDP. Run:  just probe plan-safety
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_RULES = Path(__file__).resolve().parent.parent / ".fux" / "rules"

# Files that make up the plan plane: the design doc, the template, every instance.
_EXPLICIT = ["secure-holdings-plan.md", "portfolio-plan-template.md"]

# Each pattern marks a data-plane leak that must never reach a committed plan doc.
_LEAKS: dict[str, re.Pattern[str]] = {
    "currency amount": re.compile(r"(?:₹|Rs\.?|INR)\s*\d"),
    "grouped number (₹/qty)": re.compile(r"\d{1,3}(?:,\d{2,3})+"),
    "long id / quantity": re.compile(r"\b\d{7,}\b"),
    "broker secret": re.compile(r"\b(enctoken|access_token|api[_-]?key|client_id|client_code)\b", re.I),
}


def scan_text(text: str) -> list[tuple[int, str, str]]:
    """Return (line_no, leak_label, snippet) for every data-plane leak found."""
    hits: list[tuple[int, str, str]] = []
    for n, line in enumerate(text.splitlines(), 1):
        for label, rx in _LEAKS.items():
            m = rx.search(line)
            if m:
                hits.append((n, label, line.strip()[:80]))
    return hits


def _plan_docs() -> list[Path]:
    seen: dict[Path, None] = {}
    for name in _EXPLICIT:
        seen[_RULES / name] = None
    for pattern in ("*.plan.md", "*.drift.md"):
        for p in sorted(_RULES.glob(pattern)):
            seen[p] = None
    return [p for p in seen if p.exists()]


def main() -> int:
    leaked = False
    for path in _plan_docs():
        hits = scan_text(path.read_text(encoding="utf-8"))
        rel = path.relative_to(_RULES.parent.parent)
        if hits:
            leaked = True
            for line_no, label, snippet in hits:
                print(f"✗ {rel}:{line_no}  [{label}]  {snippet}")
        else:
            print(f"✓ {rel}  clean")
    if leaked:
        print("\n❌ plan-plane leak — these docs are NOT safe for a public repo.", file=sys.stderr)
        return 1
    print("\n✅ all plan docs are strategy-only — safe to commit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
