"""Fetch secrets from the alpha-forge-bach vault into os.environ.

Called by env_loader after dotenv files are loaded, so the AFBACH_TOKEN from
.env.cred.local is available. Vault values override file values.

Behavior:
    - No AFBACH_TOKEN set → no-op (file-based env still works).
    - Vault unreachable → log and continue (file env is the fallback).
    - Vault locked → log warning; `vault_locked()` returns True so callers
      can surface a helpful "run afbach unlock" message instead of a cryptic
      "env var not set" error.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

_DEFAULT_URL = "http://[::1]:54087/v1"
_TIMEOUT = 5

_vault_locked: bool = False


def vault_locked() -> bool:
    """True when AFBACH_TOKEN is set but the vault responded with 503 (locked)."""
    return _vault_locked


def load_from_vault(*, override: bool = True) -> int:
    """Pull all secrets for this app's namespace into os.environ.

    Returns the number of keys injected. Returns 0 (silent) when AFBACH_TOKEN is
    unset — that path lets .env.cred.local keep working during migration.
    """
    global _vault_locked
    _vault_locked = False

    token = os.getenv("AFBACH_TOKEN")
    if not token:
        return 0

    url = os.getenv("AFBACH_URL", _DEFAULT_URL).rstrip("/")
    req = urllib.request.Request(
        f"{url}/secrets",
        headers={"Authorization": f"Bearer {token}"},
    )

    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            payload = json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 403:
            raise RuntimeError("afbach: invalid AFBACH_TOKEN") from e
        if e.code == 503:
            _vault_locked = True
            msg = "afbach: vault is locked — run `afbach unlock` or POST /v1/unlock"
            if os.getenv("APP_ENV", "development") != "development":
                raise RuntimeError(msg) from e
            logger.warning(msg)
            return 0
        raise RuntimeError(f"afbach: HTTP {e.code}") from e
    except (urllib.error.URLError, TimeoutError) as e:
        logger.warning("afbach: vault unreachable at %s (%s) — using file env", url, e)
        return 0

    secrets: dict[str, str] = payload.get("secrets", {})
    injected = 0
    for k, v in secrets.items():
        if override or k not in os.environ:
            os.environ[k] = v
            injected += 1
    logger.info("afbach: loaded %d secrets from %s", injected, url)
    return injected
