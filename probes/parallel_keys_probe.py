"""Verify the Parallel (parallel.ai) API key is provisioned in the afbach vault.

The signals-engine grounding toggle (docs/signals-engine.handoff.md §9) calls
Parallel's Search API, and per the two-place-secrets rule that key lives only in
the alpha-forge-bach vault — never env or code.

Keys are *always* provisioned through bach itself (the single source of truth) —
never by this probe:

    afbach secret set anton PARALLEL_API_KEY

This probe is the verification counterpart: it reads the vault over bach's HTTP
API and asserts each Parallel key is present and non-empty, so grounding_service
and `/health/boot` can rely on it at runtime. Secret VALUES are never printed —
only key names and a masked length.

Run:
    just probe parallel-keys
    uv run python probes/parallel_keys_probe.py

Requires: afbach vault running + unlocked, AFBACH_TOKEN/AFBACH_URL (env or
.env.cred.local). Standalone — no CDP, no backend.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _probe_auth import vault_endpoint

# Parallel keys the signals engine needs. Search API is the default grounding
# path (§9); add the Task API key here if handoff Q3 is answered "yes".
PARALLEL_KEYS = ("PARALLEL_API_KEY",)

_results: list[tuple[str, bool, str]] = []


def _record(label: str, ok: bool, detail: str = "") -> None:
    _results.append((label, ok, detail))
    print(f"  {'✓' if ok else '✗'}  {label}" + (f"  {detail}" if detail else ""))


def _vault_secrets(url: str, token: str) -> dict[str, str]:
    req = urllib.request.Request(f"{url}/secrets", headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read()).get("secrets", {})


def _verify(secrets: dict[str, str], key: str) -> None:
    value = secrets.get(key)
    if value:
        _record(f"{key}: provisioned in vault", True, f"set · {len(value)} chars")
    elif key in secrets:
        _record(f"{key}: present but empty", False, f"re-run `afbach secret set anton {key}`")
    else:
        _record(f"{key}: missing", False, f"run `afbach secret set anton {key}`")


def main() -> int:
    url, token = vault_endpoint()
    print(f"Parallel Keys Probe  →  afbach vault [{url}]")
    if not token:
        print("  ✗  no AFBACH_TOKEN (env or .env.cred.local) — cannot reach vault")
        return 1
    try:
        secrets = _vault_secrets(url, token)
        for key in PARALLEL_KEYS:
            _verify(secrets, key)
    except urllib.error.HTTPError as e:
        hint = " — run `afbach unlock`" if e.code == 503 else ""
        print(f"  ✗  vault error: HTTP {e.code}{hint}")
        return 1
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"  ✗  vault unreachable at {url} ({e})")
        return 1

    passed = sum(1 for _, ok, _ in _results if ok)
    print(f"\n── Summary\n  {passed}/{len(_results)} Parallel keys provisioned in bach")
    return 0 if all(ok for _, ok, _ in _results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
