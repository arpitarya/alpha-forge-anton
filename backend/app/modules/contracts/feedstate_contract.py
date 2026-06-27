"""Feed liveness — so the UI never presents stale or pending data as fresh.

`honest-pending` is the whole point: a feed that has not ticked yet is `state="stale"`
with `last_tick=None` — **never a faked live 0%**. Any metric derived from a non-live feed
must carry `| None` (pending) downstream rather than defaulting to 0; this model is the
signal that lets the UI render "—" instead of inventing a number.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

FeedStatus = Literal["live", "stale"]


class FeedState(BaseModel):
    """Liveness of a data feed. `last_tick=None` = honest-pending (never a faked 0)."""

    state: FeedStatus = "stale"
    last_tick: datetime | None = None
    reason: str = ""
