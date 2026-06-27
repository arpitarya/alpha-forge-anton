"""Integrity manifest for the raw NSE cache — counts + hashes only (PII-safe, NOT committed).

Lives at `nse_data_dir()/cache-manifest.json`. Per cached file it records {sha256, byte_size,
row_count, source_url, fetched_at}; plus `missing` days (known 404s, so a resume skips them).
A day is "done" only if both its files exist AND their bytes still sha256-match the manifest — mere
existence never counts, so a partial/corrupt file is re-fetched. `verify_all` re-hashes every file
for a no-network audit; `rollup` is the one-glance whole-cache fingerprint.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field

from app.modules.marketdata.bhavcopy_ingest import nse_data_dir
from app.modules.marketdata.bhavcopy_integrity import sha256_hex

_MANIFEST = "cache-manifest.json"


def eq_name(day: str) -> str:
    return f"eq-{day}.zip"


def idx_name(day: str) -> str:
    return f"idx-{day}.csv"


class CacheEntry(BaseModel):
    sha256: str
    byte_size: int
    row_count: int
    source_url: str
    fetched_at: str


class Rollup(BaseModel):
    day_count: int
    date_range: list[str]
    total_bytes: int
    cache_fingerprint: str


class CacheManifest(BaseModel):
    files: dict[str, CacheEntry] = Field(default_factory=dict)
    missing: list[str] = Field(default_factory=list)

    def record(self, name: str, blob: bytes, url: str, rows: int) -> None:
        self.files[name] = CacheEntry(
            sha256=sha256_hex(blob), byte_size=len(blob), row_count=rows,
            source_url=url, fetched_at=datetime.now(UTC).isoformat(),
        )

    def is_done(self, day: str) -> bool:
        for name in (eq_name(day), idx_name(day)):
            e = self.files.get(name)
            p = nse_data_dir() / name
            if e is None or not p.exists() or sha256_hex(p.read_bytes()) != e.sha256:
                return False
        return True

    def verify_all(self) -> list[str]:
        """Re-hash every recorded file vs the manifest; return names that are missing/corrupt."""
        bad = []
        for name, e in sorted(self.files.items()):
            p = nse_data_dir() / name
            if not p.exists() or sha256_hex(p.read_bytes()) != e.sha256:
                bad.append(name)
        return bad

    def rollup(self) -> Rollup:
        days = sorted({n.split("-", 1)[1].rsplit(".", 1)[0] for n in self.files})
        fp = sha256_hex("".join(self.files[n].sha256 for n in sorted(self.files)).encode())
        return Rollup(
            day_count=len(days), date_range=[days[0], days[-1]] if days else [],
            total_bytes=sum(e.byte_size for e in self.files.values()), cache_fingerprint=fp,
        )


def manifest_path() -> Path:
    return nse_data_dir() / _MANIFEST


def load() -> CacheManifest:
    p = manifest_path()
    if not p.exists():
        return CacheManifest()
    return CacheManifest.model_validate_json(p.read_text(encoding="utf-8"))


def save(man: CacheManifest) -> None:
    data = man.model_dump()
    data["missing"] = sorted(set(man.missing))
    data["rollup"] = man.rollup().model_dump()
    manifest_path().write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
