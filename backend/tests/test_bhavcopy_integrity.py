"""bhavcopy_integrity — sha256, zip CRC, in-memory zip read, eq/idx validation, atomic write."""

from __future__ import annotations

import io
import zipfile

import pytest

from app.modules.marketdata.bhavcopy_integrity import (
    atomic_write,
    eq_rowcount,
    idx_ok,
    sha256_hex,
    zip_crc_ok,
    zip_text,
)

_EQ = "SYMBOL,SERIES,CLOSE,TOTTRDVAL\nRELIANCE,EQ,2500,3e9\nTCS,EQ,3800,3e9\n"
_IDX = "Index Name,Closing Index Value\nNifty 50,21741.9\n"


def _zip(text: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("bhav.csv", text)
    return buf.getvalue()


def test_sha256_is_deterministic() -> None:
    assert sha256_hex(b"abc") == sha256_hex(b"abc") != sha256_hex(b"abd")


def test_zip_crc_and_text() -> None:
    blob = _zip(_EQ)
    assert zip_crc_ok(blob) and not zip_crc_ok(b"not-a-zip")
    assert "RELIANCE" in zip_text(blob)


def test_eq_rowcount_and_failures() -> None:
    assert eq_rowcount(_zip(_EQ), "2024-01-02") == 2
    with pytest.raises(ValueError):  # corrupt
        eq_rowcount(b"garbage", "2024-01-02")
    with pytest.raises(ValueError):  # zero equity rows
        eq_rowcount(_zip("SYMBOL,SERIES,CLOSE\nX,GB,1\n"), "2024-01-02")


def test_idx_ok() -> None:
    assert idx_ok(_IDX.encode()) == 1
    with pytest.raises(ValueError):
        idx_ok(b"Index Name,Closing Index Value\nNifty Bank,48000\n")


def test_atomic_write_leaves_no_temp(tmp_path) -> None:
    dst = tmp_path / "eq-2024-01-02.zip"
    atomic_write(dst, b"hello")
    assert dst.read_bytes() == b"hello"
    assert list(tmp_path.glob(".tmp-*")) == []  # no half-file left behind
    atomic_write(dst, b"world")  # overwrite is atomic
    assert dst.read_bytes() == b"world"
