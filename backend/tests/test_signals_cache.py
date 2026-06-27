"""signals_cache_dir — env override, home default, and dir creation."""

from __future__ import annotations

from app.core.paths import data_dir
from app.modules.signals.cache_utils import signals_cache_dir


def test_env_override_is_used_and_created(tmp_path, monkeypatch) -> None:
    target = tmp_path / "signals-cache"
    monkeypatch.setenv("SIGNALS_CACHE_DIR", str(target))
    got = signals_cache_dir()
    assert got == target
    assert got.is_dir()  # created on resolve


def test_tilde_is_expanded(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))  # keep the expansion out of the real home dir
    monkeypatch.setenv("SIGNALS_CACHE_DIR", "~/sc")
    assert signals_cache_dir() == tmp_path / "sc"


def test_falls_back_to_data_dir_default_when_unset(monkeypatch) -> None:
    monkeypatch.delenv("SIGNALS_CACHE_DIR", raising=False)
    assert signals_cache_dir() == data_dir() / "signals-cache"  # $ANTON_DATA_DIR/signals-cache
