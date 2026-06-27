"""cache_manifest — record/is_done (byte-verified), verify_all, rollup fingerprint, load/save."""

from __future__ import annotations

import pytest

from app.modules.marketdata import cache_manifest as cm
from app.modules.marketdata.bhavcopy_ingest import nse_data_dir
from app.modules.marketdata.bhavcopy_integrity import atomic_write


@pytest.fixture(autouse=True)
def _tmp_cache(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("NSE_DATA_DIR", str(tmp_path / "nse"))


def _seed(man: cm.CacheManifest, day: str) -> bytes:
    eq = f"eq-bytes-{day}".encode()
    atomic_write(nse_data_dir() / cm.eq_name(day), eq)
    man.record(cm.eq_name(day), eq, "url", 5)
    idx = f"idx-bytes-{day}".encode()
    atomic_write(nse_data_dir() / cm.idx_name(day), idx)
    man.record(cm.idx_name(day), idx, "url", 1)
    return eq


def test_is_done_requires_byte_match() -> None:
    man = cm.CacheManifest()
    _seed(man, "2016-01-04")
    assert man.is_done("2016-01-04")  # both files present + sha matches
    assert not man.is_done("2016-01-05")  # never recorded
    (nse_data_dir() / cm.eq_name("2016-01-04")).write_bytes(b"tampered")
    assert not man.is_done("2016-01-04")  # existence alone never counts


def test_verify_all_flags_corruption() -> None:
    man = cm.CacheManifest()
    _seed(man, "2016-01-04")
    assert man.verify_all() == []
    (nse_data_dir() / cm.idx_name("2016-01-04")).write_bytes(b"bad")
    assert man.verify_all() == [cm.idx_name("2016-01-04")]


def test_rollup_fingerprint_is_content_addressed() -> None:
    man = cm.CacheManifest()
    _seed(man, "2016-01-04")
    _seed(man, "2016-01-05")
    r = man.rollup()
    assert r.day_count == 2 and r.date_range == ["2016-01-04", "2016-01-05"]
    fp1 = man.rollup().cache_fingerprint
    _seed(man, "2016-01-06")
    assert man.rollup().cache_fingerprint != fp1  # changes when the cache changes


def test_load_save_round_trip() -> None:
    man = cm.CacheManifest()
    _seed(man, "2016-01-04")
    cm.save(man)
    again = cm.load()
    assert again.files.keys() == man.files.keys()
    assert again.is_done("2016-01-04")
