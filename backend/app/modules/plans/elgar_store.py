"""Store-root access for the few raw files elgar's doc API doesn't serve as `.md`
docs — `plans/mandate.json` and `edges-journal/journal.jsonl`.

The root is obtained FROM elgar (`elgar path`) and cached — Anton never derives it
from `ANTON_DATA_DIR`; elgar maintains the store + path (ADR `anton-delegates-elgar-store`).
A bad/unreachable store raises `ElgarStoreError` — fail-loud, never a silent fallback.
"""

from __future__ import annotations

import subprocess
from functools import lru_cache
from pathlib import Path

from app.modules.plans.elgar_bridge import ElgarStoreError, _bin


@lru_cache(maxsize=1)
def store_root() -> Path:
    """The elgar store root, as reported by `elgar path`. Raises if unreachable."""
    try:
        p = subprocess.run([_bin(), "path"], capture_output=True, text=True)  # noqa: S603
    except OSError as e:
        raise ElgarStoreError(f"elgar path failed: {e}") from e
    root = p.stdout.strip()
    if p.returncode != 0 or not root or not Path(root).is_dir():
        raise ElgarStoreError(f"elgar store unreachable: {(p.stdout or p.stderr)[:200]}")
    return Path(root)
