"""Resolve probe credentials from environment or afbach vault.

Priority:
  1. PROBE_USER / PROBE_PASS env vars (explicit override)
  2. afbach vault keys PROBE_USER / PROBE_PASS (Wagner user credentials)
  3. Error — no hardcoded fallbacks

Usage:
    from _probe_auth import probe_credentials
    username, password = probe_credentials()
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path


def _vault_secret(key: str) -> str | None:
    token = os.getenv("AFBACH_TOKEN")
    if not token:
        # Try reading from .env.cred.local relative to repo root
        cred_file = Path(__file__).resolve().parent.parent / ".env.cred.local"
        if cred_file.exists():
            for line in cred_file.read_text().splitlines():
                if line.startswith("AFBACH_TOKEN="):
                    token = line.split("=", 1)[1].strip()
                if line.startswith("AFBACH_URL="):
                    os.environ.setdefault("AFBACH_URL", line.split("=", 1)[1].strip())
    if not token:
        return None

    url = os.getenv("AFBACH_URL", "http://[::1]:54087/v1").rstrip("/")
    req = urllib.request.Request(
        f"{url}/secrets",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            payload = json.loads(r.read())
        return payload.get("secrets", {}).get(key)
    except Exception:
        return None


def probe_credentials() -> tuple[str, str]:
    """Return (username, password) for UI probes — sourced from Wagner user credentials."""
    username = os.getenv("PROBE_USER") or _vault_secret("PROBE_USER")
    password = os.getenv("PROBE_PASS") or _vault_secret("PROBE_PASS")
    if not username or not password:
        raise RuntimeError(
            "Cannot resolve probe credentials. "
            "Set PROBE_USER/PROBE_PASS env vars or store them in the afbach vault."
        )
    return username, password
