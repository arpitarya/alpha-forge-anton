"""Provenance manifest for the committed offline panel — the `data_provenance` record.

The one-time ingestion run writes a `Manifest` next to the panel JSON: which official NSE
archives were read, when, over what date range, how many sessions and symbols, and **every
missing day** (a 404 archive is recorded honestly, never interpolated). This is what a
Phase-1b `TestReport` reads to stamp `data_provenance = nse-bhavcopy (real)`. Counts + URLs
only — no holdings, no ₹ PII — so it is constitutionally safe to commit.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field


class Manifest(BaseModel):
    """Audit record of one ingestion run + the panel it produced."""

    source: str = "nse-bhavcopy"
    fetched_at: str  # ISO-8601 UTC of the run
    from_date: str  # ISO
    to_date: str  # ISO
    sessions: int = 0  # trading days actually cached
    symbol_count: int = 0  # symbols in the built panel universe
    source_urls: list[str] = Field(default_factory=list)
    missing_days: list[str] = Field(default_factory=list)  # archives 404 / unavailable


def write_manifest(manifest: Manifest, path: Path) -> Path:
    """Write the manifest as pretty, stable-ordered JSON (deterministic for diffs)."""
    path.write_text(
        json.dumps(manifest.model_dump(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def load_manifest(path: Path) -> Manifest:
    """Read an existing manifest (so a re-run extends it rather than discarding history)."""
    return Manifest.model_validate_json(path.read_text(encoding="utf-8"))
