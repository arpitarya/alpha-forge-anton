"""progress_utils.Progress — renders only on a TTY, stderr-only, byte-identical when off."""

from __future__ import annotations

import io

from app.modules.marketdata.progress_utils import Progress


class _Tty(io.StringIO):
    """A StringIO that claims to be a terminal — lets us assert the rendered line offline."""

    def isatty(self) -> bool:
        return True


def test_off_tty_writes_nothing() -> None:
    plain = io.StringIO()  # isatty() is False ⇒ a piped/CI stream
    p = Progress("NSE 2016", 261, enabled=True, stream=plain)
    p.update(142, "2016-07-22", "cached 130 · ⬇ 12 · ⚠ 3")
    p.close()
    assert plain.getvalue() == ""  # nothing on a non-terminal — guarantees byte-identical pipes


def test_quiet_writes_nothing_even_on_tty() -> None:
    tty = _Tty()
    p = Progress("NSE 2016", 261, enabled=False, stream=tty)  # --quiet
    p.update(1, "2016-01-04", "cached 0 · ⬇ 1 · ⚠ 0")
    assert tty.getvalue() == ""


def test_tty_renders_the_bar_line() -> None:
    tty = _Tty()
    p = Progress("NSE 2016", 261, enabled=True, stream=tty)
    p.update(142, "2016-07-22", "cached 130 · ⬇ 12 · ⚠ 3")
    out = tty.getvalue()
    assert out.startswith("\r")  # carriage-return overwrite, never a new line per tick
    assert "NSE 2016 ▕" in out and "▏ 142/261 · 54% · 2016-07-22" in out
    assert "cached 130 · ⬇ 12 · ⚠ 3" in out and "left" in out
    assert "█" in out and "░" in out  # block bar
    assert not out.endswith("\n")  # the line stays open until close()
    p.close()
    assert tty.getvalue().endswith("\n")  # close drops to a fresh line for the ✅ summary
