"""elgar store-guard probe — a write to a bad/unreachable store FAILS LOUD, never silently.

Standalone (no CDP, no real store): points `ELGAR_BIN` at a stub that exits non-zero
(an unreachable/invalid elgar store) and asserts the architecture from
ADR `anton-delegates-elgar-store`:
  • `elgar_bridge.save` raises `ElgarStoreError` — never returns silently,
  • the real write path (`objective_tuning.apply`) propagates that raise,
  • reads degrade to None (lenient) rather than crashing,
  • REGRESSION: no `~/anton-data/elgar` fallback dir is ever created (the old bug),
  • Anton exposes no `app.core.paths.elgar_dir` (it owns no store path).

Run:  just probe elgar-store-guard   |   uv run python probes/elgar_store_guard_probe.py
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "backend"))

import app.core.paths as paths
from app.modules.plans import elgar_bridge
from app.modules.signals import objective_tuning

_FALLBACK = Path("~/anton-data/elgar").expanduser()  # the dir the old bug wrote to
_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def _stub_bin(exit_code: int) -> str:
    """A fake `elgar` CLI that always exits with `exit_code` (simulates an unreachable store)."""
    fd, path = tempfile.mkstemp(prefix="elgar-stub-", suffix=".sh")
    os.write(fd, f"#!/bin/sh\nexit {exit_code}\n".encode())
    os.close(fd)
    os.chmod(path, 0o700)  # owner-only exec — enough to run the stub
    return path


async def _run() -> None:
    fallback_existed = _FALLBACK.exists()
    os.environ["ELGAR_BIN"] = _stub_bin(1)  # every elgar call now fails
    elgar_bridge._read_cache.clear()

    check("paths exposes no elgar_dir (Anton owns no store path)", not hasattr(paths, "elgar_dir"))

    raised = False
    try:
        await elgar_bridge.save("objective", "x", collection="strategy")
    except elgar_bridge.ElgarStoreError:
        raised = True
    check("save() to an unreachable store raises ElgarStoreError", raised)

    apply_raised = False
    try:
        await objective_tuning.apply({"monthly_target_inr": 1234.0})
    except elgar_bridge.ElgarStoreError:
        apply_raised = True
    check("objective_tuning.apply propagates the fail-loud raise", apply_raised)

    check("read on a bad store degrades to None (no crash)",
          elgar_bridge.get_sync("objective", collection="strategy") is None)

    # REGRESSION: Anton must never have created the old anton-data/elgar fallback dir.
    check("no ~/anton-data/elgar fallback dir created by the write attempts",
          fallback_existed or not _FALLBACK.exists(),
          f"{_FALLBACK} was created")


def main() -> int:
    asyncio.run(_run())
    print("\n" + ("❌ elgar store-guard FAILED" if _fail
                  else "✅ elgar store-guard: writes fail loud, no silent local fallback"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
