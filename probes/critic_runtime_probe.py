"""Runtime money/PII critic probe — the enforcement behind the `runtime-note-pii` rule.

Attempts a FORBIDDEN runtime action — Orff appending a note carrying a hard identifier
(PAN / Aadhaar / account number) into the persisted `orff-context` memory doc — and asserts
the deterministic guard REFUSES it before the elgar save runs. The runtime twin of the
`plan-safety` probe (which guards the commit boundary); this guards the live write boundary.

Also asserts a clean note passes (the guard must not block legitimate context) and that the
elgar save is never reached on a blocked note (no write escapes).

Standalone — no backend, no CDP, no elgar. Run:  just probe critic-runtime
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


# Forbidden notes — each must be refused by the deterministic guard (mirrors dante BLOCK tier).
_FORBIDDEN = [
    ("PAN", "please remember my PAN is ABCDE1234F for tax filing"),
    ("Aadhaar", "my aadhaar 1234 5678 9012 — keep it handy"),
    ("account number", "save my zerodha folio: 1234567 in context"),
]
# Allowed notes — legitimate strategy/preference context; must NOT be blocked.
_ALLOWED = [
    "I prefer a large-cap value tilt with quarterly rebalancing",
    "target equity allocation around 60 percent, debt 30, gold 10",
]


def main() -> int:
    from app.modules.concierge.critic_guard import ForbiddenRuntimeActionError
    from app.modules.concierge.memory_service import append_memory

    async def run() -> None:
        # The elgar save must NEVER be reached on a forbidden note — mock it to catch any escape.
        save = AsyncMock(return_value="elgar://plan/orff-context")
        with patch("app.modules.plans.elgar_bridge.save", save), \
             patch("app.modules.concierge.memory_service.load_memory",
                   AsyncMock(return_value="")):
            # 1. Every forbidden note is refused BEFORE the write.
            for label, note in _FORBIDDEN:
                before = save.await_count
                try:
                    await append_memory(note)
                    check(f"forbidden note refused ({label})", False, "write was NOT blocked")
                except ForbiddenRuntimeActionError as e:
                    blocked_no_write = (e.kind == "money/PII"
                                        and save.await_count == before)
                    check(f"forbidden note refused ({label})", blocked_no_write,
                          "raised but elgar save still ran" if save.await_count != before else "")

            # 2. No forbidden note ever reached the store.
            check("no forbidden write escaped to elgar", save.await_count == 0,
                  f"{save.await_count} unexpected save(s)")

            # 3. A clean note passes and DOES write (guard must not block legitimate context).
            for note in _ALLOWED:
                before = save.await_count
                try:
                    await append_memory(note)
                    check("clean note allowed", save.await_count == before + 1,
                          "clean note did not write")
                except ForbiddenRuntimeActionError:
                    check("clean note allowed", False, "legitimate note was wrongly blocked")

    asyncio.run(run())

    if _fail:
        print(f"\n❌ runtime critic: {_fail} check(s) failed — a forbidden action slipped or a "
              "clean one was blocked.", file=sys.stderr)
        return 1
    print("\n✅ runtime critic: forbidden money/PII notes refused at the write boundary; "
          "clean notes pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
