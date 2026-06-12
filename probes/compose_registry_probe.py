"""Compose-registry sync guard — prompt = validator = client whitelist.

The composable vocabulary lives in `compose_registry.COMPOSABLE_COMPONENTS`
(backend) and the `WHITELIST` map in `compose.registry.ts` (client). If they
drift, the model is prompted with components the client silently drops — the
exact failure this probe exists to prevent (see `ui-component-contract`).
Also asserts every composable name is a real solar-ui export and that the
composable spec checker accepts/rejects correctly.

Standalone — no backend server, no CDP. Run:  just probe compose-registry
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

_fail = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global _fail
    print(f"{'✓' if ok else '✗'} {name}{('  — ' + detail) if detail and not ok else ''}")
    if not ok:
        _fail += 1


def client_whitelist() -> set[str]:
    src = (ROOT / "frontend/src/modules/concierge/compose.registry.ts").read_text()
    body = src.split("WHITELIST", 1)[1]
    return set(re.findall(r"^\s{2}(\w+),$", body, re.MULTILINE))


def solar_exports() -> set[str]:
    src = (ROOT / "packages/solar-ui/src/index.ts").read_text()
    names: set[str] = set()
    for m in re.finditer(r"^export (?:\{([^}]+)\}|type)", src, re.MULTILINE):
        if m.group(1):
            names.update(n.strip() for n in m.group(1).split(","))
    return {n for n in names if n}


def main() -> int:
    from app.modules.concierge.compose_registry import (
        COMPOSABLE_COMPONENTS,
        COMPOSABLE_HOOKS,
        composable_errors,
    )

    wl = client_whitelist()
    check("client WHITELIST == backend COMPOSABLE_COMPONENTS", wl == set(COMPOSABLE_COMPONENTS),
          f"only-client={sorted(wl - COMPOSABLE_COMPONENTS)} only-backend={sorted(COMPOSABLE_COMPONENTS - wl)}")

    exports = solar_exports()
    missing = sorted(COMPOSABLE_COMPONENTS - exports)
    check("every composable is a solar-ui export", not missing, f"missing={missing}")

    hooks_src = "".join(p.read_text() for p in (ROOT / "frontend/src/modules").rglob("*.ts*"))
    missing_hooks = sorted(h for h in COMPOSABLE_HOOKS if f"function {h}(" not in hooks_src)
    check("every composable hook exists in frontend", not missing_hooks, f"missing={missing_hooks}")

    good = {"component": "Card", "children": [
        {"component": "Stat", "props": {"label": "GOLD"}, "data": "useProjection"}]}
    check("valid spec passes composable check", composable_errors(good) == [])
    bad = {"component": "AccountSection", "data": "useAuthStore"}
    check("foreign component + hook rejected", len(composable_errors(bad)) == 2)

    print("\n" + ("❌ compose registry drift" if _fail else "✅ compose vocabulary is in sync"))
    return 1 if _fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
