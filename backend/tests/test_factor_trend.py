"""Dual-momentum trend filter — NIFTY vs its 200-DMA (cash when below or unconfirmed)."""

from __future__ import annotations

from app.modules.edges.factor_trend import nifty_above_200dma, sma


def test_sma_needs_full_window() -> None:
    assert sma([float(i) for i in range(199)], 198) is None  # < 200 points
    rising = [float(i) for i in range(1, 210)]
    assert sma(rising, 208) == sum(rising[9:209]) / 200


def test_above_and_below() -> None:
    rising = [float(i) for i in range(1, 210)]  # close (209) well above its 200-DMA
    assert nifty_above_200dma(rising, 208) is True
    falling = [float(210 - i) for i in range(210)]  # close (2) well below its 200-DMA
    assert nifty_above_200dma(falling, 208) is False
    assert nifty_above_200dma(rising, 150) is False  # history < 200 → cash (unconfirmed)
