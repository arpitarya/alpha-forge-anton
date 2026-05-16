"""Print Groww free cash via CDP capture of /margin/user_margin_details.

Attaches to the existing AlphaForge Chrome (port 9299), opens a fresh tab to
`groww.in/user/balance/inr`, captures the margin XHR, and prints `CASH.value`.

Run while Groww is logged in:
    just groww-chrome   # if needed
    uv run python probes/groww_cash_probe.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers.groww.groww_cash_helper import capture_groww_cash


async def main() -> None:
    cash = await capture_groww_cash(timeout_seconds=30.0)
    print(f"Groww free cash (CASH.value from margin/user_margin_details): ₹{cash:,.2f}")


if __name__ == "__main__":
    asyncio.run(main())
