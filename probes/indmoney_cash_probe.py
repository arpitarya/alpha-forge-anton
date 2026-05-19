"""Print INDmoney free USD cash via CDP capture of /account/basic.

Attaches to the existing AlphaForge Anton Chrome (port 9299), opens a fresh tab to
the US-stocks holdings page, captures the account/basic XHR, and prints
`cash_available_for_trade` (USD).

Run while INDmoney is logged in:
    uv run python probes/indmoney_cash_probe.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers.indmoney.indmoney_cash_helper import capture_indmoney_cash


async def main() -> None:
    cash = await capture_indmoney_cash(timeout_seconds=30.0)
    print(f"INDmoney free cash (cash_available_for_trade): ${cash:,.2f}")


if __name__ == "__main__":
    asyncio.run(main())
