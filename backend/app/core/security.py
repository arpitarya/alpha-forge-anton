"""Security utilities — JWT token validation."""

from __future__ import annotations

import jwt

from app.core.config import settings


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
