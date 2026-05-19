"""Print Zerodha free cash via /oms/user/margins (HTTP, enctoken-based).

Uses the cached enctoken from .alpha-forge-anton/sessions. No CDP needed.

Run:
    uv run python probes/zerodha_cash_probe.py
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.modules.brokers.zerodha.zerodha_source_helper import (
    acquire_enctoken,
    fetch_margins_json,
)


async def main() -> None:
    enctoken = await acquire_enctoken()
    data = await fetch_margins_json(enctoken)
    equity = (data.get("equity") or {})
    cash = float((equity.get("available") or {}).get("cash") or 0.0)

    print(f"Zerodha free cash (equity.available.cash): ₹{cash:,.2f}\n")
    print("Full equity.available shape:")
    print(json.dumps(equity.get("available"), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
