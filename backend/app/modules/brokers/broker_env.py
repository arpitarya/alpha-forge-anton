"""Vault-aware env helpers shared by all broker source helpers.

Two public helpers replace copy-pasted patterns across every broker:

  source_ready(REQUIRED_ENV, env)  — replaces the __init__ READY check
  require_env("KEY", env)          — raises with vault context if key missing
"""

from __future__ import annotations

import logging
from typing import Callable

from app.core.vault_client import vault_locked

logger = logging.getLogger(__name__)

_UNLOCK_HINT = "run `afbach unlock` or POST http://[::1]:54087/v1/unlock"
_STORE_HINT = "store it in the afbach vault: PUT /v1/secrets {{\"key\": \"{key}\", \"value\": \"<value>\"}}"


def source_ready(required_keys: tuple[str, ...], env_fn: Callable[[str], str]) -> bool:
    """Return True when every required key is set; log a vault hint if not."""
    missing = [k for k in required_keys if not env_fn(k)]
    if not missing:
        return True
    if vault_locked():
        logger.warning(
            "Source UNCONFIGURED — vault is locked, cannot load: %s. %s",
            ", ".join(missing), _UNLOCK_HINT,
        )
    return False


def require_env(key: str, env_fn: Callable[[str], str]) -> str:
    """Return the env value for *key*, or raise with vault context if missing."""
    v = env_fn(key)
    if v:
        return v
    if vault_locked():
        raise RuntimeError(f"{key} not loaded — vault is locked. {_UNLOCK_HINT}")
    raise RuntimeError(f"{key} not found — {_STORE_HINT.format(key=key)}")
