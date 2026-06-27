"""The cross-sectional data panel — aligned daily closes for the universe + NIFTF.

A `Panel` is the survivorship-safe, point-in-time price matrix the factor engine ranks over:
ISO `dates`, a `{symbol: closes}` map aligned 1:1 with those dates, and the NIFTY index series
(for the 200-DMA trend filter). The source is injectable via `PanelProvider`: EB-0 runs on a
committed offline fixture (deterministic, $0); a real cached NSE snapshot drops in later by
shipping a different JSON — no code change.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Panel:
    dates: list[str]  # ISO trading dates
    closes: dict[str, list[float]]  # symbol → closes aligned 1:1 with dates
    nifty: list[float]  # NIFTY index aligned 1:1 with dates

    def symbols(self) -> list[str]:
        return sorted(self.closes)


class PanelProvider(Protocol):
    async def panel(self) -> Panel: ...


def load_panel(path: Path) -> Panel:
    """Read a committed offline panel JSON ({dates, closes, nifty})."""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    return Panel(dates=d["dates"], closes=d["closes"], nifty=d["nifty"])


class FixturePanelProvider:
    """Serve a committed panel JSON — the offline, deterministic EB-0 data source."""

    def __init__(self, path: Path) -> None:
        self._path = path

    async def panel(self) -> Panel:
        return load_panel(self._path)
