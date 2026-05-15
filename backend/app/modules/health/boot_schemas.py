"""Pydantic schemas for the /health/boot endpoint that drives the terminal's
boot splash. One row per real backend system; the frontend renders them in
declaration order."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class BootStatus(str, Enum):
    OK = "ok"          # green check
    WARN = "warn"      # amber — reachable but not fully configured
    ERROR = "error"    # red — probe failed
    SKIP = "skip"      # grey — not applicable on this host


class BootService(BaseModel):
    key: str           # stable identifier ("backend", "database", "zerodha", …)
    label: str         # one-line description shown on the splash
    status: BootStatus
    detail: str        # short status text on the right (latency, "ready", error)


class BootReport(BaseModel):
    services: list[BootService]
