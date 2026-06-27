"""`just ingest-nse FROM TO` — parallel, resumable, byte-integrity NSE ingestion ($0, stdlib).

A `ThreadPoolExecutor` over business days (resume skips verified-good days; each day validated +
atomically written; a `Breaker` throttles on 429/403). Fetch order/workers never change the bytes.
"""

from __future__ import annotations

import argparse
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

from app.modules.marketdata import bhavcopy_fetch as fetch
from app.modules.marketdata import cache_manifest as cm
from app.modules.marketdata.bhavcopy_service import Outcome, ingest_day
from app.modules.marketdata.progress_utils import Progress
from app.modules.marketdata.throttle_utils import Breaker

_SAVE_EVERY = 50  # periodic manifest checkpoint, so an interrupt loses ≤ this many days of resume


def _days(frm: str, to: str):
    d, end = date.fromisoformat(frm), date.fromisoformat(to)
    while d <= end:
        if d.weekday() < 5:  # Mon-Fri; holidays simply 404 → recorded missing
            yield d.isoformat()
        d += timedelta(days=1)


def _detail(t: dict, w: int) -> str:
    return (f"cached {t[Outcome.CACHED]} · ⬇ {t[Outcome.FETCHED]} · ♻ {t[Outcome.REFETCHED]} · ⚠ "
            f"{t[Outcome.MISSING]} · ✗ {t[Outcome.FAILED]} · w {w}")


def _verify(man: cm.CacheManifest) -> int:
    r, bad = man.rollup(), man.verify_all()
    print(f"cache: {r.day_count} days · {r.total_bytes} bytes · fp {r.cache_fingerprint[:12]}")
    print(f"❌ {len(bad)} corrupt/missing: {bad[:8]}" if bad else "✅ cache matches the manifest")
    return 1 if bad else 0


def run(frm: str, to: str, raw_dir: Path | None, workers: int, quiet: bool) -> dict:
    man, days = cm.load(), list(_days(frm, to))
    opener = None if raw_dir else fetch.make_opener()
    if opener is not None:
        fetch.prime(opener)
    breaker, prog = Breaker(workers), Progress(f"NSE {frm[:4]}", len(days), enabled=not quiet)
    lock, tally, done = threading.Lock(), dict.fromkeys(Outcome, 0), [0]

    def work(day: str) -> None:
        if opener is not None:
            breaker.acquire()
        status, outcome, recs = 200, Outcome.FAILED, []
        try:
            outcome, recs, status = ingest_day(day, opener, raw_dir, man)
        except Exception:
            outcome, status = Outcome.FAILED, 200
        finally:
            if opener is not None:
                breaker.release(status)
        with lock:
            if status == 403 and opener is not None:
                fetch.prime(opener)
            for rec in recs:
                man.record(*rec)
            if outcome is Outcome.MISSING:
                man.missing.append(day)
            tally[outcome] += 1
            done[0] += 1
            if done[0] % _SAVE_EVERY == 0:
                cm.save(man)
            prog.update(done[0], day, _detail(tally, breaker.permits))

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(work, days))
    prog.close()
    cm.save(man)
    print(f"✅ [{frm}, {to}] {len(days)} days — {_detail(tally, breaker.permits)}")
    return tally


def main() -> int:
    p = argparse.ArgumentParser(description="Parallel resumable NSE bhavcopy ingestion.")
    p.add_argument("frm", metavar="FROM")
    p.add_argument("to", metavar="TO")
    p.add_argument("--raw-dir", type=Path, default=None, help="ingest local archives (no network)")
    p.add_argument("--workers", type=int, default=int(os.getenv("NSE_WORKERS", "8")))
    p.add_argument("--quiet", "--no-progress", action="store_true", dest="quiet")
    p.add_argument("--verify", action="store_true", help="re-hash cache vs manifest; no network")
    a = p.parse_args()
    if a.verify:
        return _verify(cm.load())
    return 1 if run(a.frm, a.to, a.raw_dir, a.workers, a.quiet)[Outcome.FAILED] else 0


if __name__ == "__main__":
    raise SystemExit(main())
