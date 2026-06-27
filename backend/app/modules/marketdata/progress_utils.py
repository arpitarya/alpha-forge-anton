"""Thread-safe stdlib `\r` STDERR progress bar — a `Lock` guards the render so concurrent worker
threads never interleave a half-written line. Renders ONLY on a TTY and not silenced (piped/CI runs
stay byte-identical; never touches stdout / manifest / panel). `update()` each tick, `close()`
once (prints a newline so a following summary line stays intact). No deps.
"""

from __future__ import annotations

import sys
import threading
import time

_BAR_W = 15


def _mmss(secs: float) -> str:
    m, s = divmod(int(secs), 60)
    return f"{m}:{s:02d}"


class Progress:
    def __init__(self, label: str, total: int, *, enabled: bool, stream=sys.stderr) -> None:
        self.label, self.total, self.stream = label, max(total, 1), stream
        self.enabled = enabled and stream.isatty()
        self._start = time.monotonic()
        self._lock = threading.Lock()

    def update(self, current: int, item: str, detail: str = "") -> None:
        if not self.enabled:
            return
        frac = min(current / self.total, 1.0)
        bar = "█" * round(_BAR_W * frac) + "░" * (_BAR_W - round(_BAR_W * frac))
        elapsed = time.monotonic() - self._start
        eta = elapsed / current * (self.total - current) if current else 0.0
        tail = f" · {detail}" if detail else ""
        line = (
            f"{self.label} ▕{bar}▏ {current}/{self.total} · {int(frac * 100)}% · {item}{tail}"
            f" · {_mmss(elapsed)} ~{_mmss(eta)} left"
        )
        with self._lock:
            self.stream.write("\r\x1b[K" + line)
            self.stream.flush()

    def close(self) -> None:
        if self.enabled:
            with self._lock:
                self.stream.write("\n")
                self.stream.flush()
