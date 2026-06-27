"""panel_build on the raw-zip cache — per-rebalance superset, determinism, byte-integrity Gate-0.

Cache scenario (10 sessions, weekly step 5 → rebalances at t=0 and t=5): AAA/BBB liquid throughout;
CCC liquid days 0-2 then delists (kept, ffilled); DDD illiquid (excluded); EEE lists day 3, in by
t=5 (reconstitution). Seeds the NEW cache directly — eq-{day}.zip + idx-{day}.csv + the sha256
cache-manifest — exactly what the parallel ingest writes.
"""

from __future__ import annotations

import io
import json
import zipfile

import pytest

from app.modules.marketdata import cache_manifest as cm
from app.modules.marketdata.bhavcopy_ingest import nse_data_dir
from app.modules.marketdata.bhavcopy_integrity import atomic_write
from app.modules.marketdata.gate0_integrity import Gate0Error
from app.modules.marketdata.panel_build import build

_DAYS = [f"2024-01-{d:02d}" for d in range(1, 11)]
_HDR = "SYMBOL,SERIES,OPEN,HIGH,LOW,CLOSE,TOTTRDQTY,TOTTRDVAL\n"


def _zip_csv(text: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("bhav.csv", text)
    return buf.getvalue()


def _seed_cache() -> None:
    man = cm.CacheManifest()
    for i, day in enumerate(_DAYS):
        liq = {"AAA": (100 + i, 1000.0), "BBB": (100 + i, 900.0), "DDD": (100 + i, 100.0)}
        if i <= 2:
            liq["CCC"] = (500 + i, 500.0)  # delists after day 2
        if i >= 3:
            liq["EEE"] = (50 + i, 2000.0)  # lists day 3
        body = "".join(f"{s},EQ,{c},{c},{c},{c},100,{t}\n" for s, (c, t) in liq.items())
        eq = _zip_csv(_HDR + body)
        atomic_write(nse_data_dir() / cm.eq_name(day), eq)
        man.record(cm.eq_name(day), eq, "t", len(liq))
        idx = f"Index Name,Closing Index Value\nNifty 50,{21000 + i}\n".encode()
        atomic_write(nse_data_dir() / cm.idx_name(day), idx)
        man.record(cm.idx_name(day), idx, "t", 1)
    cm.save(man)


@pytest.fixture(autouse=True)
def _tmp_cache(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("NSE_DATA_DIR", str(tmp_path / "nse"))


def test_superset_reconstitutes_keeps_delisted_excludes_illiquid(tmp_path) -> None:
    _seed_cache()
    panel = build("2024-01-01", "2024-01-10", top_n=3, out=tmp_path / "out")
    assert sorted(panel["closes"]) == ["AAA", "BBB", "CCC", "EEE"]  # DDD illiquid-excluded
    assert panel["turnover"]["CCC"] == [500, 500, 500, 0, 0, 0, 0, 0, 0, 0]  # 0-filled off-trading
    assert panel["closes"]["CCC"] == [500, 501, 502, 502, 502, 502, 502, 502, 502, 502]  # ffill


def test_gzip_determinism(tmp_path) -> None:
    _seed_cache()
    out = tmp_path / "out"
    build("2024-01-01", "2024-01-10", top_n=3, out=out)
    gz = out / "panel.json.gz"
    assert gz.exists() and not (out / "panel.json").exists()
    first = gz.read_bytes()
    build("2024-01-01", "2024-01-10", top_n=3, out=out)
    assert gz.read_bytes() == first  # byte-identical (gzip mtime=0)


def test_build_refuses_corrupt_cache(tmp_path) -> None:
    _seed_cache()
    (nse_data_dir() / cm.eq_name("2024-01-04")).write_bytes(b"corrupt-not-the-recorded-bytes")
    with pytest.raises(Gate0Error):  # byte-integrity Gate-0: sha mismatch → refuse to build
        build("2024-01-01", "2024-01-10", top_n=3, out=tmp_path / "out")


def test_exclusions_drop_symbol_from_superset(tmp_path) -> None:
    from app.modules.edges.factor_universe import Exclusions

    _seed_cache()
    excl = Exclusions(symbols=frozenset({"AAA"}), source="dummy")  # dummy symbol, not a real ticker
    panel = build("2024-01-01", "2024-01-10", top_n=3, out=tmp_path / "out", exclusions=excl)
    assert "AAA" not in panel["closes"]
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["sessions"] == 10
