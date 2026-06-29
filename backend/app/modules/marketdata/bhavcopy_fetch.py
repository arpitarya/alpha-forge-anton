"""Network layer for the one-time NSE ingestion — STDLIB urllib, cookie-primed, backoff + jitter.

NSE blocks non-browser agents, so we prime cookies from the home page (once, shared across worker
threads via a single opener over a thread-safe `CookieJar`) with a realistic browser User-Agent.
`fetch_bytes` retries 429/403/5xx with exponential backoff + jitter and returns the HTTP status so
the CLI's circuit-breaker can react; 404 → `None` (an honest missing day). It also paces each GET by
`NSE_REQUEST_DELAY` seconds (+jitter, default 0 = off) so a low-`--workers` run stays polite enough
that NSE never throttles a large historical backfill. UDiFF is authoritative from 2024-07; legacy
cm-bhav covers older dates. The ONLY networked module — downstream is offline.
"""

from __future__ import annotations

import os
import random
import time
import urllib.error
import urllib.request
from datetime import date
from http.cookiejar import CookieJar

_BASE = "https://nsearchives.nseindia.com"
UDIFF = _BASE + "/content/cm/BhavCopy_NSE_CM_0_0_0_{ymd}_F_0000.csv.zip"
CM_BHAV = _BASE + "/content/historical/EQUITIES/{yyyy}/{mon}/cm{dd}{mon}{yyyy}bhav.csv.zip"
IND_CLOSE = _BASE + "/content/indices/ind_close_all_{dmy}.csv"
HOME = "https://www.nseindia.com/"
UDIFF_FROM = "2024-07-08"
ALL_URLS = [UDIFF, CM_BHAV, IND_CLOSE]
_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)
_HEADERS = [("User-Agent", _UA), ("Accept", "*/*"), ("Accept-Language", "en-US,en;q=0.9")]
_RETRY = {429, 403, 500, 502, 503, 504}
_PACE = max(0.0, float(os.getenv("NSE_REQUEST_DELAY", "0") or 0))  # seconds before each GET (+jitter)


def _parts(day: str) -> dict[str, str]:
    d = date.fromisoformat(day)
    return {
        "ymd": d.strftime("%Y%m%d"), "dmy": d.strftime("%d%m%Y"), "yyyy": d.strftime("%Y"),
        "mon": d.strftime("%b").upper(), "dd": d.strftime("%d"),
    }


def make_opener() -> urllib.request.OpenerDirector:
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    op.addheaders = _HEADERS
    return op


def prime(opener: urllib.request.OpenerDirector) -> None:
    """Seed NSE cookies from the home page so archive requests are not blocked."""
    try:
        opener.open(HOME, timeout=30).read()
    except urllib.error.URLError:
        pass


def fetch_bytes(opener, url: str, retries: int = 4) -> tuple[bytes | None, int]:
    """GET, backoff+jitter on 429/403/5xx; 404→(None,404); ok→(bytes,200); gave-up→(None,code)."""
    last = 0
    for attempt in range(retries):
        if _PACE:
            time.sleep(_PACE + random.uniform(0, _PACE))  # noqa: S311  politeness pace (non-crypto)
        try:
            with opener.open(url, timeout=60) as r:
                return r.read(), 200
        except urllib.error.HTTPError as e:
            last = e.code
            if e.code == 404:
                return None, 404
            if e.code not in _RETRY:
                return None, e.code
        except urllib.error.URLError:
            last = -1
        if attempt < retries - 1:
            time.sleep((2**attempt) + random.uniform(0, 1.0))  # noqa: S311  backoff + jitter (non-crypto)
    return None, last


def eq_urls(day: str) -> list[str]:
    p = _parts(day)
    order = [UDIFF, CM_BHAV] if day >= UDIFF_FROM else [CM_BHAV, UDIFF]
    return [u.format(**p) for u in order]


def idx_url(day: str) -> str:
    return IND_CLOSE.format(**_parts(day))
