"""Per-provider token-bucket rate limiter."""

from __future__ import annotations

import asyncio
import time


class TokenBucket:
    """Refills `rate` tokens per second up to `capacity`."""

    def __init__(self, capacity: float, rate: float) -> None:
        self._capacity = capacity
        self._rate = rate
        self._tokens = capacity
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        now = time.monotonic()
        delta = now - self._last_refill
        self._tokens = min(self._capacity, self._tokens + delta * self._rate)
        self._last_refill = now

    async def acquire(self, tokens: float = 1.0) -> None:
        async with self._lock:
            self._refill()
            if self._tokens < tokens:
                wait = (tokens - self._tokens) / self._rate
                await asyncio.sleep(wait)
                self._refill()
            self._tokens -= tokens

    @property
    def available(self) -> float:
        self._refill()
        return self._tokens


# Default per-provider limits (requests per minute → tokens/sec)
_LIMITS: dict[str, tuple[float, float]] = {
    "gemini":      (60.0,  1.0),   # 60 rpm free tier
    "groq":        (30.0,  0.5),   # 30 rpm free tier
    "openrouter":  (20.0,  0.33),
    "huggingface": (10.0,  0.17),
    "cerebras":    (30.0,  0.5),
    "mistral":     (60.0,  1.0),
    "deepseek":    (60.0,  1.0),
    "claude-sdk":  (5.0,   0.08),
}


class RateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, TokenBucket] = {
            name: TokenBucket(cap, rate)
            for name, (cap, rate) in _LIMITS.items()
        }

    async def acquire(self, provider: str) -> None:
        bucket = self._buckets.get(provider)
        if bucket:
            await bucket.acquire()

    def remaining(self, provider: str) -> float | None:
        bucket = self._buckets.get(provider)
        return bucket.available if bucket else None
