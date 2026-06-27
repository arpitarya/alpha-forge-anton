"""NSE ingest — offline acceptance: raw-zip cache, resume, self-heal, --verify, byte-integrity.

Standalone (no network, no store). Stages the committed fixtures as raw NSE archives (equity .zip +
index .csv) in a temp `--raw-dir`, then drives the real parallel CLI offline and asserts: a fresh
fetches both days + leaves no temp file; a re-run downloads ZERO (resume on byte-verified days);
corrupting one cached zip re-fetches EXACTLY that day; `--verify` flags a planted corruption + exits
non-zero (no network); `build-panel` REFUSES a hash-mismatched cache; the cache fingerprint is
independent of `--workers`; and `panel.json.gz` is byte-identical across builds.

Run:  just probe nse-ingest   |   uv run python probes/nse_ingest_probe.py
"""

from __future__ import annotations

import os
import sys
import tempfile
import zipfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "backend"))

_FIX = _ROOT / "backend" / "tests" / "fixtures" / "bhavcopy_raw"
_DAYS = [("20240102", "02012024"), ("20240103", "03012024")]
FROM, TO = "2024-01-02", "2024-01-03"
_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def _raw_dir(tmp: Path) -> Path:
    d = tmp / "raw"
    d.mkdir()
    eq, idx = (_FIX / "udiff_sample.csv").read_text(), (_FIX / "ind_close_sample.csv").read_text()
    for ymd, dmy in _DAYS:
        with zipfile.ZipFile(d / f"BhavCopy_NSE_CM_0_0_0_{ymd}_F_0000.csv.zip", "w") as zf:
            zf.writestr("bhav.csv", eq)
        (d / f"ind_close_all_{dmy}.csv").write_text(idx)
    return d


def main() -> int:
    from app.modules.marketdata import cache_manifest as cm
    from app.modules.marketdata.bhavcopy_cli import _verify, run
    from app.modules.marketdata.bhavcopy_ingest import nse_data_dir
    from app.modules.marketdata.bhavcopy_service import Outcome
    from app.modules.marketdata.gate0_integrity import Gate0Error
    from app.modules.marketdata.panel_build import build

    tmp = Path(tempfile.mkdtemp())
    os.environ["NSE_DATA_DIR"] = str(tmp / "nse")
    raw, out = _raw_dir(tmp), tmp / "out"

    t1 = run(FROM, TO, raw, 4, True)
    check("fresh run fetches both days", t1[Outcome.FETCHED] == 2, str(dict(t1)))
    check("atomic write leaves no temp file", not list(nse_data_dir().glob(".tmp-*")))
    check("re-run downloads ZERO (resume)", run(FROM, TO, raw, 4, True)[Outcome.CACHED] == 2)

    eq02 = nse_data_dir() / cm.eq_name("2024-01-02")
    eq03_mtime = (nse_data_dir() / cm.eq_name("2024-01-03")).stat().st_mtime_ns
    eq02.write_bytes(b"corrupt-bytes")
    t3 = run(FROM, TO, raw, 4, True)
    check("corrupt day re-fetched (self-heal)", t3[Outcome.REFETCHED] == 1)
    untouched = (nse_data_dir() / cm.eq_name("2024-01-03")).stat().st_mtime_ns == eq03_mtime
    check("only the corrupt day was touched", untouched)

    eq02.write_bytes(b"corrupt-again")
    check("--verify flags corruption, exit≠0 (no network)", _verify(cm.load()) == 1)
    refused = False
    try:
        build(FROM, TO, 250, out)
    except Gate0Error:
        refused = True
    check("build REFUSES hash-mismatched cache", refused)

    run(FROM, TO, raw, 4, True)  # heal
    fp4 = cm.load().rollup().cache_fingerprint
    os.environ["NSE_DATA_DIR"] = str(tmp / "nse1")  # fresh cache, single worker
    run(FROM, TO, raw, 1, True)
    check("cache fingerprint independent of --workers", cm.load().rollup().cache_fingerprint == fp4)

    panel = build(FROM, TO, 250, out)
    check("panel built from verified cache", sorted(panel["closes"]) == ["RELIANCE", "TCS"])
    first = (out / "panel.json.gz").read_bytes()
    build(FROM, TO, 250, out)
    again = (out / "panel.json.gz").read_bytes()
    check("panel.json.gz byte-identical across builds", again == first)

    ok = "✅ nse-ingest: raw-zip cache · resume · self-heal · --verify · byte-integrity · deterministic"  # noqa: E501
    print("\n" + ("❌ nse-ingest FAILED" if _fail else ok))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
