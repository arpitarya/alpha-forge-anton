"""Byte-integrity primitives for the raw NSE cache — sha256, zip CRC, atomic write, validation.

Stdlib only. `atomic_write` lands bytes via a temp file in the SAME dir then `os.replace`, so an
interrupted download never leaves a half-file at the real path (it can't be mistaken for cached).
`eq_rowcount` proves an equity zip opens, every member CRC verifies, and it parses to non-empty
equity rows; `idx_ok` proves the index csv carries the NIFTY-50 close. These turn "the file exists"
into "the bytes are good" — the basis of resume + the byte-integrity Gate-0.
"""

from __future__ import annotations

import hashlib
import io
import os
import tempfile
import zipfile
from pathlib import Path

from app.modules.marketdata.bhavcopy_parse import parse_index_close, parse_raw


def sha256_hex(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def zip_crc_ok(blob: bytes) -> bool:
    """True iff the zip opens, is non-empty, and every member's CRC verifies (`testzip`)."""
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            return bool(zf.namelist()) and zf.testzip() is None
    except zipfile.BadZipFile:
        return False


def zip_text(blob: bytes) -> str:
    """Decode the first member of a zip in-memory (never unzipped to disk)."""
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        return zf.read(zf.namelist()[0]).decode("utf-8", "replace")


def eq_rowcount(blob: bytes, day: str) -> int:
    """Equity rows in a zip; raises `ValueError` if the zip is corrupt or parses to zero bars."""
    if not zip_crc_ok(blob):
        raise ValueError("equity zip failed CRC / is empty")
    rows = parse_raw(zip_text(blob), day)
    if not rows:
        raise ValueError("equity zip parsed to zero rows")
    return len(rows)


def idx_ok(blob: bytes) -> int:
    """Return 1 if the index csv carries the NIFTY-50 close, else raise `ValueError`."""
    if parse_index_close(blob.decode("utf-8", "replace")) is None:
        raise ValueError("index csv missing the NIFTY-50 close")
    return 1


def atomic_write(path: Path, blob: bytes) -> None:
    """Write bytes atomically: temp in the same dir → fsync → `os.replace` (chmod 600)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp-", suffix=path.suffix)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(blob)
            fh.flush()
            os.fsync(fh.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
