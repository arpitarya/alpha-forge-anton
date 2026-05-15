#!/usr/bin/env python3
"""Polls /health/boot and prints a live status table to the dev terminal.

Runs as the 'monitor' process in the Procfile so it appears alongside
backend/frontend output. Reprints on startup, on state change, and whenever
the backend comes back online after a uvicorn reload.
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime

import httpx

BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
API_PREFIX = os.getenv("API_V1_PREFIX", "/api/v1")
BOOT_URL = f"http://localhost:{BACKEND_PORT}{API_PREFIX}/health/boot"
POLL_INTERVAL = 2  # seconds — short enough to catch post-reload state within one cycle

G = "\033[32m"   # green
Y = "\033[1;33m" # yellow bold
R = "\033[31m"   # red
C = "\033[36m"   # cyan
B = "\033[1m"    # bold
D = "\033[2m"    # dim
Z = "\033[0m"    # reset

_GLYPH = {"ok": f"{G}✓{Z}", "warn": f"{Y}⚠{Z}", "error": f"{R}✗{Z}", "skip": f"{D}–{Z}"}
_COL   = {"ok": G, "warn": Y, "error": R, "skip": D}


def _render(services: list[dict]) -> None:
    now = datetime.now().strftime("%H:%M:%S")
    ok_n  = sum(1 for s in services if s["status"] == "ok")
    total = len(services)
    all_ok = ok_n == total

    summary = f"{G}all systems go{Z}" if all_ok else f"{Y}{ok_n}/{total} healthy{Z}"
    sep = "─" * 48
    print(f"{B}{sep}{Z}", flush=True)
    print(f"{B}  AlphaForge  {D}{now}{Z}  {summary}", flush=True)
    print(f"{D}  {'KEY':<14}{'STATUS':<8}DETAIL{Z}", flush=True)

    for svc in services:
        glyph  = _GLYPH.get(svc["status"], "?")
        col    = _COL.get(svc["status"], "")
        key    = svc["key"]
        detail = svc.get("detail", "")
        label  = svc["label"]
        print(f"  {glyph}  {col}{key:<14}{Z}{D}{detail:<12}{Z}{label}", flush=True)

    print(f"{B}{sep}{Z}", flush=True)


def _state_key(services: list[dict]) -> str:
    return str([(s["key"], s["status"], s.get("detail", "")) for s in services])


async def main() -> None:
    last_key: str | None = None
    backend_down = False

    async with httpx.AsyncClient(timeout=4.0) as client:
        while True:
            try:
                resp = await client.get(BOOT_URL)
                resp.raise_for_status()
                services = resp.json().get("services", [])
                key = _state_key(services)

                if key != last_key or backend_down:
                    _render(services)
                    last_key = key
                    backend_down = False

            except Exception:  # noqa: BLE001
                if not backend_down:
                    print(f"{Y}⟳  backend reloading…{Z}", flush=True)
                    backend_down = True
                    last_key = None  # force reprint when it comes back

            await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
