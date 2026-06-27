"""The cross-sectional data panel — aligned daily closes for the universe + NIFTF.

A `Panel` is the survivorship-safe, point-in-time price matrix the factor engine ranks over:
ISO `dates`, a `{symbol: closes}` map aligned 1:1 with those dates, and the NIFTY index series
(for the 200-DMA trend filter). The source is injectable via `PanelProvider`: EB-0 runs on a
committed offline fixture (deterministic, $0); a real cached NSE snapshot drops in later by
shipping a different JSON — no code change.
"""

from __future__ import annotations

import gzip
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class Panel:
    dates: list[str]  # ISO trading dates
    closes: dict[str, list[float]]  # symbol → closes aligned 1:1 with dates
    nifty: list[float]  # NIFTY index aligned 1:1 with dates
    turnover: dict[str, list[float]] = field(default_factory=dict)  # ₹ traded value; 0 if untraded

    def symbols(self) -> list[str]:
        return sorted(self.closes)


class PanelProvider(Protocol):
    async def panel(self) -> Panel: ...


def load_panel(path: Path) -> Panel:
    """Read a panel JSON ({dates, closes, nifty, turnover?}); `.gz` is gunzipped transparently."""
    path = Path(path)
    raw = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
    d = json.loads(raw)
    return Panel(
        dates=d["dates"], closes=d["closes"], nifty=d["nifty"], turnover=d.get("turnover", {})
    )


def dump_panel(panel: dict, path: Path) -> None:
    """Write the panel as DETERMINISTIC gzip (mtime=0 ⇒ byte-identical re-runs); ~3-4 MB."""
    body = (json.dumps(panel, sort_keys=True) + "\n").encode("utf-8")
    Path(path).write_bytes(gzip.compress(body, mtime=0))


class FixturePanelProvider:
    """Serve a committed panel JSON — the offline, deterministic EB-0 data source."""

    def __init__(self, path: Path) -> None:
        self._path = path

    async def panel(self) -> Panel:
        return load_panel(self._path)
