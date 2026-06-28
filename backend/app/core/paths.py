"""Single source of truth for every filesystem path the app reads or writes.

Constitution `configurable-paths`: no module may hardcode a home-directory or
absolute filesystem path. Every path derives from `ANTON_DATA_DIR` — the
per-machine data root (default `~/.alphaforge-anton`) — and stays individually
overridable by its own documented env var. See CLAUDE.md → "Configurable paths".
"""

from __future__ import annotations

import os
from pathlib import Path

DEFAULT_DATA_DIR = "~/.alphaforge-anton"


def data_dir() -> Path:
    """Per-machine data root. Override with `ANTON_DATA_DIR` (`~` expanded)."""
    raw = os.getenv("ANTON_DATA_DIR", "").strip()
    return Path(raw or DEFAULT_DATA_DIR).expanduser()


def resolve(env_var: str, *default_suffix: str) -> Path:
    """A path under `data_dir()`, overridable by `env_var`.

    The override wins when set: an absolute (or `~`) path is used as-is, a
    relative path resolves under `data_dir()`. Unset → `data_dir()/<suffix>`.
    """
    raw = os.getenv(env_var, "").strip()
    if not raw:
        return data_dir().joinpath(*default_suffix)
    p = Path(raw).expanduser()
    return p if p.is_absolute() else data_dir() / p


# NOTE: there is deliberately no `elgar_dir()` here. The elgar store is an
# independent sibling tool that maintains its own store + path; Anton owns no
# elgar filesystem path and reaches it only through the elgar CLI API
# (`app.modules.plans.elgar_bridge`). See ADR `anton-delegates-elgar-store`.
