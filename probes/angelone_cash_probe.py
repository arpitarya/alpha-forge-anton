"""Print Angel One free cash via CDP capture of /funds/v2/getRMSLimit.

Attaches to the existing AlphaForge Anton Chrome (port 9299), opens a fresh tab to
`angelone.in/trade/funds`, captures the RMS limit XHR, and prints
`data.netAvailableFunds`.

Run while Angel One is logged in:
    uv run python probes/angelone_cash_probe.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers.angelone.angelone_cash_helper import capture_angelone_cash


async def main() -> None:
    cash = await capture_angelone_cash(timeout_seconds=30.0)
    print(f"Angel One free cash (data.netAvailableFunds): ₹{cash:,.2f}")


if __name__ == "__main__":
    asyncio.run(main())
