"""Shared vision helper — split image data URLs into (mime, base64) pairs."""

from __future__ import annotations

import re

_DATA_URL = re.compile(r"^data:(image/[\w.+-]+);base64,(.+)$", re.DOTALL)


def parse_data_url(url: str) -> tuple[str, str] | None:
    """("image/png", "<base64>") for a valid image data URL, else None."""
    m = _DATA_URL.match(url or "")
    return (m.group(1), m.group(2)) if m else None
