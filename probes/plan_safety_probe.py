"""Git-safety guard — the enforcement behind the plan-store rule.

Money documents live in the private elgar store (`elgar path`), never in this public
repo. This FAILS (exit 1) if (a) any `*.plan.md` / `*.drift.md` is git-tracked here —
those belong in the store — or (b) a committed plan-adjacent doc under `.fux/rules/`
carries data-plane figures: ₹ amounts, quantities, account/client IDs, broker secrets.
See the `plan-store` and `secure-holdings-plan` Fux entries. Dante's `pii` audit is the
repo-wide sibling of this check.

Standalone — no backend, no CDP. Run:  just probe plan-safety
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_RULES = ROOT / ".fux" / "rules"

# Committed docs that talk about plans/holdings and must stay strategy-only.
_EXPLICIT = ["secure-holdings-plan.md", "plan-store.md", "core-allocation.md"]

# Each pattern marks a data-plane leak that must never reach a committed doc.
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


def _tracked_plan_docs() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "*.plan.md", "*.drift.md"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return [line for line in out.stdout.splitlines() if line]


def main() -> int:
    failed = False
    strays = _tracked_plan_docs()
    for s in strays:
        failed = True
        print(f"✗ {s}  [plan doc tracked in repo — belongs in the elgar store]")
    if not strays:
        print("✓ no *.plan.md / *.drift.md tracked — store holds them all")
    for path in (p for n in _EXPLICIT if (p := _RULES / n).exists()):
        hits = scan_text(path.read_text(encoding="utf-8"))
        rel = path.relative_to(ROOT)
        if hits:
            failed = True
            for line_no, label, snippet in hits:
                print(f"✗ {rel}:{line_no}  [{label}]  {snippet}")
        else:
            print(f"✓ {rel}  clean")
    if failed:
        print("\n❌ plan-store leak — this repo is NOT safe to publish.", file=sys.stderr)
        return 1
    print("\n✅ plan docs live in the store; committed docs are strategy-only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
