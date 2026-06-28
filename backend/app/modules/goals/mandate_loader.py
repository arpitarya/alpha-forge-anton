"""Load the program mandate (the `Objective` contract) from the elgar store.

The mandate carries personal book ₹ amounts, so it lives ONLY in the private elgar
store (`plans/mandate.json`) and is loaded at runtime, never committed to this repo
(`plan-store`). Anton owns no store path: the root comes from elgar (`elgar_store`),
and a missing store/file RAISES (fail-loud — a bad/unreachable store surfaces, never a
silent faked default). `opex_per_month` is filled at runtime from the
`funding.subscriptions` registry; `covered` stays None (honest-pending) until a
realised-P&L source exists (Gate-4 paper).
"""

from __future__ import annotations

import json
from pathlib import Path

from app.modules.contracts.objective_contract import Objective
from app.modules.funding.funding_subscriptions import opex_per_month
from app.modules.plans.elgar_store import store_root


def _mandate_path() -> Path:
    return store_root() / "plans" / "mandate.json"


def load_mandate() -> Objective:
    """Parse `<store>/plans/mandate.json` → Objective. Raises if the store/file is absent."""
    path = _mandate_path()
    if not path.exists():
        raise FileNotFoundError(f"no mandate in elgar store: {path} (set ELGAR_DIR / `elgar list`)")
    obj = Objective.model_validate(json.loads(path.read_text(encoding="utf-8")))
    obj.self_funding.opex_per_month = opex_per_month()  # runtime: from the registry
    obj.self_funding.covered = None  # honest-pending until Gate-4 paper
    return obj


__all__ = ["load_mandate"]
