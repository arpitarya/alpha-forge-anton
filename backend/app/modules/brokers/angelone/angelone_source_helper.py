"""Angel One SmartAPI — TOTP login + holdings fetch.

Login flow: free SmartAPI app (https://smartapi.angelbroking.com). The user
registers a personal app to get an API key, then enables TOTP on their Angel
One account. AlphaForge derives the 6-digit TOTP locally from the shared
secret (never sent over the wire) and exchanges client code + MPIN + TOTP for
a jwtToken that is cached encrypted on disk.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
import pyotp

from app.core.logging import get_logger
from app.modules.brokers._http import load_session, make_client, save_session

logger = get_logger("brokers.angelone_helper")

SMART_BASE = "https://apiconnect.angelone.in"
LOGIN_PATH = "/rest/auth/angelbroking/user/v1/loginByPassword"
HOLDINGS_PATH = "/rest/secure/angelbroking/portfolio/v1/getAllHolding"
RMS_PATH = "/rest/secure/angelbroking/user/v1/getRMS"
REQUIRED_ENV: tuple[str, ...] = (
    "ANGELONE_API_KEY",
    "ANGELONE_CLIENT_ID",
    "ANGELONE_MPIN",
    "ANGELONE_TOTP_SECRET",
)


def env(key: str) -> str:
    return os.getenv(key, "").strip()


def _smartapi_headers(api_key: str, jwt: str | None = None) -> dict[str, str]:
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-UserType": "USER",
        "X-SourceID": "WEB",
        "X-ClientLocalIP": "127.0.0.1",
        "X-ClientPublicIP": "127.0.0.1",
        "X-MACAddress": "00:00:00:00:00:00",
        "X-PrivateKey": api_key,
    }
    if jwt:
        h["Authorization"] = f"Bearer {jwt}"
    return h


async def smartapi_login() -> str:
    api_key = env("ANGELONE_API_KEY")
    client_id = env("ANGELONE_CLIENT_ID")
    mpin = env("ANGELONE_MPIN")
    secret = env("ANGELONE_TOTP_SECRET")
    if not all((api_key, client_id, mpin, secret)):
        raise RuntimeError(
            "Angel One: missing one of ANGELONE_API_KEY / CLIENT_ID / MPIN / TOTP_SECRET "
            "in .env.cred.local — register a free SmartAPI app and fill these in."
        )
    totp = pyotp.TOTP(secret).now()
    body = {"clientcode": client_id, "password": mpin, "totp": totp}
    async with make_client(base_url=SMART_BASE, headers=_smartapi_headers(api_key)) as client:
        res = await client.post(LOGIN_PATH, json=body)
        res.raise_for_status()
        payload: dict[str, Any] = res.json()
    if not payload.get("status"):
        raise RuntimeError(f"Angel One login failed: {payload.get('message') or payload}")
    jwt = (payload.get("data") or {}).get("jwtToken")
    if not jwt:
        raise RuntimeError("Angel One login: response missing jwtToken")
    return str(jwt)


async def acquire_token(force: bool = False) -> str:
    cached = load_session("angelone")
    if not force and cached.get("jwt"):
        return str(cached["jwt"])
    jwt = await smartapi_login()
    save_session("angelone", {"jwt": jwt, "client_id": env("ANGELONE_CLIENT_ID")})
    logger.info("Angel One: acquired new jwtToken via SmartAPI login")
    return jwt


async def fetch_rms_json(token: str) -> dict[str, Any]:
    """GET /user/v1/getRMS → risk-management snapshot incl. available cash."""
    api_key = env("ANGELONE_API_KEY")
    headers = _smartapi_headers(api_key, jwt=token)
    async with make_client(base_url=SMART_BASE, headers=headers) as client:
        res = await client.get(RMS_PATH)
        if res.status_code in (401, 403):
            raise httpx.HTTPStatusError(
                f"jwt rejected ({res.status_code})", request=res.request, response=res
            )
        res.raise_for_status()
        payload: dict[str, Any] = res.json()
    if not payload.get("status"):
        raise RuntimeError(f"Angel One RMS failed: {payload.get('message') or payload}")
    return dict(payload.get("data") or {})


async def fetch_holdings_json(token: str) -> list[dict[str, Any]]:
    api_key = env("ANGELONE_API_KEY")
    headers = _smartapi_headers(api_key, jwt=token)
    async with make_client(base_url=SMART_BASE, headers=headers) as client:
        res = await client.get(HOLDINGS_PATH)
        if res.status_code in (401, 403):
            raise httpx.HTTPStatusError(
                f"jwt rejected ({res.status_code})", request=res.request, response=res
            )
        res.raise_for_status()
        payload: dict[str, Any] = res.json()
    if not payload.get("status"):
        raise RuntimeError(f"Angel One holdings failed: {payload.get('message') or payload}")
    data = payload.get("data") or {}
    return list(data.get("holdings") or [])
