#!/usr/bin/env python3
"""Standalone, throttle-proof NSE bhavcopy downloader (stdlib only, no deps).

Serial + polite (so NSE never throttles), resumable (skips files already on disk), cookie-primed.
Per business day it pulls the equity bhavcopy zip (UDiFF for 2024-07-08+, else legacy cm-bhav) and
the ind_close index csv, trying each known URL form across two NSE archive hosts before giving up.
Files are saved under --out with NSE's ORIGINAL filenames, so they feed straight into the existing
offline ingest:  just ingest-nse FROM TO --raw-dir <out>  (keeps UDiFF/cm-bhav format + Gate-0).

A 404 on every candidate = NSE has no file for that day (a holiday) → recorded, not an error.
Throttle/network exhaustion → written to failed.txt so a re-run retries only those.

--out defaults to $NSE_DATA_DIR (resolved like the app: env → .env.local → .env, else
$ANTON_DATA_DIR/nse, else ~/.alphaforge-anton/nse). Raw archive names (compact dates) never collide
with the pipeline's normalized eq-/idx-/bhavcopy- files (dashed ISO), so sharing the dir is safe.

Usage:
    python scripts/fetch_bhavcopy.py 2016-01-01 2016-12-31           # → $NSE_DATA_DIR
    just ingest-nse 2016-01-01 2016-12-31 --raw-dir "$NSE_DATA_DIR"  # normalize into the cache
"""
from __future__ import annotations

import argparse
import os
import random
import time
import urllib.error
import urllib.request
from datetime import date, timedelta
from http.cookiejar import CookieJar
from pathlib import Path

HOSTS = ("https://nsearchives.nseindia.com", "https://archives.nseindia.com")
HOME = "https://www.nseindia.com/"
UDIFF_FROM = "2024-07-08"
RETRY = {429, 403, 500, 502, 503, 504}
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
REPO_ROOT = Path(__file__).resolve().parent.parent


def _env(key: str) -> str:
    """env var, else first hit in .env.local then .env (mirrors how the app reads NSE_DATA_DIR)."""
    if (v := os.getenv(key, "").strip()):
        return v
    for name in (".env.local", ".env"):
        f = REPO_ROOT / name
        if not f.exists():
            continue
        for line in f.read_text().splitlines():
            s = line.strip()
            if s.startswith("#") or "=" not in s:
                continue
            k, _, val = s.partition("=")
            if k.strip() == key:
                return val.split(" #")[0].strip().strip('"').strip("'")
    return ""


def _nse_data_dir() -> Path:
    """$NSE_DATA_DIR resolved like app.core.paths: absolute→as-is, relative/unset→under data root."""
    root = Path(_env("ANTON_DATA_DIR") or "~/.alphaforge-anton").expanduser()
    raw = _env("NSE_DATA_DIR")
    if not raw:
        return root / "nse"
    p = Path(raw).expanduser()
    return p if p.is_absolute() else root / p


def _parts(d: date) -> dict[str, str]:
    return {"ymd": d.strftime("%Y%m%d"), "dmy": d.strftime("%d%m%Y"), "yyyy": d.strftime("%Y"),
            "mon": d.strftime("%b").upper(), "dd": d.strftime("%d"), "ddmonyyyy": d.strftime("%d%b%Y").upper()}


def _eq_paths(p: dict[str, str], iso: str) -> list[str]:
    udiff = f"/content/cm/BhavCopy_NSE_CM_0_0_0_{p['ymd']}_F_0000.csv.zip"
    cmbhav = f"/content/historical/EQUITIES/{p['yyyy']}/{p['mon']}/cm{p['dd']}{p['mon']}{p['yyyy']}bhav.csv.zip"
    return [udiff, cmbhav] if iso >= UDIFF_FROM else [cmbhav, udiff]


def _candidates(iso: str) -> tuple[list[str], list[str]]:
    p = _parts(date.fromisoformat(iso))
    eq = [h + path for path in _eq_paths(p, iso) for h in HOSTS]
    idx = [h + f"/content/indices/ind_close_all_{p['dmy']}.csv" for h in HOSTS]
    return eq, idx


def _make_opener() -> urllib.request.OpenerDirector:
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))
    op.addheaders = [("User-Agent", UA), ("Accept", "*/*"), ("Accept-Language", "en-US,en;q=0.9")]
    return op


def _prime(op: urllib.request.OpenerDirector) -> None:
    try:
        op.open(HOME, timeout=30).read()
    except urllib.error.URLError:
        pass


def _get(op, url: str, delay: float, retries: int) -> tuple[bytes | None, int]:
    last = 0
    for attempt in range(retries):
        time.sleep(delay + random.uniform(0, delay))  # noqa: S311  politeness, non-crypto
        try:
            with op.open(url, timeout=60) as r:
                return r.read(), 200
        except urllib.error.HTTPError as e:
            last = e.code
            if e.code == 404:
                return None, 404
            if e.code == 403:
                _prime(op)
            if e.code not in RETRY:
                return None, e.code
        except urllib.error.URLError:
            last = -1
        time.sleep((2 ** attempt) + random.uniform(0, 1.0))  # noqa: S311  backoff
    return None, last


def _have(out: Path, p: dict[str, str], *, index: bool) -> bool:
    toks = (p["ymd"], p["dmy"], p["ddmonyyyy"])
    for f in out.glob("*"):
        if ("ind_close" in f.name.lower()) == index and any(t in f.name.upper() for t in toks):
            return True
    return False


def _fetch_one(op, urls: list[str], out: Path, delay: float, retries: int) -> int:
    """Try candidates in order. 200 → save & return 200; all-404 → 404; else last error code."""
    status = 404
    for url in urls:
        blob, st = _get(op, url, delay, retries)
        if blob is not None:
            (out / os.path.basename(url)).write_bytes(blob)
            return 200
        status = st if st != 404 else status
    return status


def _days(frm: str, to: str):
    d, end = date.fromisoformat(frm), date.fromisoformat(to)
    while d <= end:
        if d.weekday() < 5:
            yield d.isoformat()
        d += timedelta(days=1)


def run(frm: str, to: str, out: Path, delay: float, retries: int) -> int:
    out.mkdir(parents=True, exist_ok=True)
    op = _make_opener()
    _prime(op)
    days = list(_days(frm, to))
    fetched = cached = holiday = 0
    failed: list[str] = []
    for i, iso in enumerate(days, 1):
        p = _parts(date.fromisoformat(iso))
        eq_urls, idx_urls = _candidates(iso)
        eq = 200 if _have(out, p, index=False) else _fetch_one(op, eq_urls, out, delay, retries)
        idx = 200 if _have(out, p, index=True) else _fetch_one(op, idx_urls, out, delay, retries)
        if eq == 200 and idx == 200:
            fetched += 1
        elif eq == 404 and idx == 404:
            holiday += 1
        elif _have(out, p, index=False) and _have(out, p, index=True):
            cached += 1
        else:
            failed.append(iso)
        print(f"\r{i}/{len(days)} {iso} · ⬇{fetched} ♻{cached} ·{holiday}holiday ✗{len(failed)}",
              end="", flush=True)
    print()
    if failed:
        (out / "failed.txt").write_text("\n".join(failed) + "\n")
        print(f"⚠ {len(failed)} days unfetched (throttle/network) → {out / 'failed.txt'} — re-run to retry")
    print(f"✅ [{frm}, {to}] {len(days)} business days → {out}  (⬇{fetched} ♻{cached} ·{holiday}holiday ✗{len(failed)})")
    return 1 if failed else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Standalone polite NSE bhavcopy downloader (stdlib).")
    ap.add_argument("frm", metavar="FROM")
    ap.add_argument("to", metavar="TO")
    ap.add_argument("--out", type=Path, default=None, help="output dir (default: $NSE_DATA_DIR)")
    ap.add_argument("--delay", type=float, default=1.0, help="base seconds between requests (+jitter)")
    ap.add_argument("--retries", type=int, default=4)
    a = ap.parse_args()
    out = a.out or _nse_data_dir()
    print(f"→ saving to {out}")
    return run(a.frm, a.to, out, a.delay, a.retries)


if __name__ == "__main__":
    raise SystemExit(main())
