"""Adaptive concurrency breaker — halve inflight + pause on a 429/403 burst (anti-ban). Stdlib.

A `Condition`-guarded inflight limiter shared by the worker threads: `acquire()` blocks until a slot
frees AND we're not in a cool-down; `release(status)` counts 429/403 hits and, on a burst, **halves
the permit ceiling** and sets a global pause. 200s slowly heal the hit count. It sits on top of the
`ThreadPoolExecutor` so effective concurrency can drop below the worker count without restarting it.
"""

from __future__ import annotations

import threading
import time

_BURST = 3  # consecutive-ish throttles before halving
_COOLDOWN = 30.0  # seconds to pause after a throttle


class Breaker:
    def __init__(self, workers: int) -> None:
        self._cv = threading.Condition()
        self._permits = max(1, workers)
        self._inflight = 0
        self._paused_until = 0.0
        self._hits = 0

    def acquire(self) -> None:
        with self._cv:
            while self._inflight >= self._permits or time.monotonic() < self._paused_until:
                self._cv.wait(timeout=0.5)
            self._inflight += 1

    def release(self, status: int) -> None:
        with self._cv:
            self._inflight -= 1
            if status in (429, 403):
                self._hits += 1
                self._paused_until = time.monotonic() + _COOLDOWN
                if self._hits >= _BURST and self._permits > 1:
                    self._permits = max(1, self._permits // 2)
                    self._hits = 0
            elif status == 200:
                self._hits = max(0, self._hits - 1)
            self._cv.notify_all()

    @property
    def permits(self) -> int:
        with self._cv:
            return self._permits
