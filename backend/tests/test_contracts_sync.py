"""The contract drift guard — checked-in TS must equal a fresh codegen.

If a Pydantic contract model changes without `just contracts-gen` being re-run, the
checked-in `frontend/src/modules/contracts/*.ts` diverges from `emit_ts(...)` and this
test fails. That is the whole point: the backend models and the frontend types cannot
silently drift.
"""

from __future__ import annotations

import pytest

from app.modules.contracts import contracts_codegen as cg


@pytest.mark.parametrize("model, stem", cg.MODELS, ids=[s for _, s in cg.MODELS])
def test_ts_matches_model(model: type, stem: str) -> None:
    path = cg._OUT / f"{stem}.types.ts"
    assert path.exists(), f"missing generated type file: {path} — run `just contracts-gen`"
    on_disk = path.read_text(encoding="utf-8")
    assert on_disk == cg.emit_ts(model), f"{stem}.types.ts stale; run `just contracts-gen`"


def test_barrel_matches() -> None:
    path = cg._OUT / "index.ts"
    assert path.read_text(encoding="utf-8") == cg._barrel(), (
        "index.ts stale — run `just contracts-gen`"
    )
