"""Progress-bar probe — TTY renders the bar, non-TTY is silent (deterministic), stderr only.

Standalone (no network, no store, no real terminal): drives `progress_utils.Progress` against a
faux-TTY `StringIO` and a plain one, asserting the exact rendered line on a terminal and **nothing
at all** off a terminal (the guarantee that piped / CI ingest runs stay byte-identical). The live
ingest bar is the same `Progress` wired into `bhavcopy_cli.run`; `just probe nse-ingest` (piped)
proves it stays silent there.

Run:  just probe progress   |   uv run python probes/progress_probe.py
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "backend"))

from app.modules.marketdata.progress_utils import Progress  # noqa: E402

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


class _Tty(io.StringIO):
    def isatty(self) -> bool:
        return True


def main() -> int:
    plain = io.StringIO()  # not a terminal
    Progress("NSE 2016", 261, enabled=True, stream=plain).update(142, "2016-07-22", "cached 130")
    check("off-TTY writes nothing (piped runs byte-identical)", plain.getvalue() == "")

    quiet = _Tty()
    Progress("NSE 2016", 261, enabled=False, stream=quiet).update(1, "2016-01-04", "x")
    check("--quiet writes nothing even on a TTY", quiet.getvalue() == "")

    tty = _Tty()
    p = Progress("NSE 2016", 261, enabled=True, stream=tty)
    p.update(142, "2016-07-22", "cached 130 · ⬇ 12 · ⚠ 3")
    out = tty.getvalue()
    check("TTY renders a \\r block-bar status line", out.startswith("\r") and "▕" in out
          and "█" in out and "░" in out)
    check("line carries count/%/date/detail", "142/261 · 54% · 2016-07-22" in out
          and "cached 130 · ⬇ 12 · ⚠ 3" in out and "left" in out)
    check("tick keeps the line open (no newline)", not out.endswith("\n"))
    p.close()
    check("close() drops to a fresh line", tty.getvalue().endswith("\n"))
    if out:
        print(f"   sample: {out.strip()}")

    # thread-safety: many workers hammering update() must never raise nor interleave a half line.
    import threading

    ct = _Tty()
    cp = Progress("cc", 400, enabled=True, stream=ct)
    threads = [threading.Thread(target=lambda i=i: [cp.update(i, "d", "x") for _ in range(50)])
               for i in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    lines = [seg for seg in ct.getvalue().split("\r") if seg]
    check("concurrent update() is lock-safe (every render is a whole line)",
          all(s.startswith("\x1b[K") and "left" in s for s in lines), f"{len(lines)} renders")

    ok = "✅ progress: TTY bar renders, off-TTY silent, thread-safe"
    print("\n" + ("❌ progress FAILED" if _fail else ok))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
