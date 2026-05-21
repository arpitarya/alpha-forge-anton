"""Print Binance free USD/USDT cash via CDP capture of wallet/balance.

Attaches to the existing AlphaForge Anton Chrome (port 9299), opens a fresh tab to
the spot wallet page, captures the wallet/balance XHR, and prints the summed
free balance across stablecoins (USDT/USDC/BUSD/FDUSD).

Field path: data[].asset == 'USDT' (etc.) → data[].free.
This must be re-confirmed if Binance changes the response shape.

Run while Binance is logged in:
    uv run python probes/binance_cash_probe.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers.binance.binance_cash_helper import capture_binance_cash


async def main() -> None:
    cash = await capture_binance_cash(timeout_seconds=30.0)
    print(f"Binance free cash (stablecoin sum): ${cash:,.2f}")


if __name__ == "__main__":
    asyncio.run(main())
