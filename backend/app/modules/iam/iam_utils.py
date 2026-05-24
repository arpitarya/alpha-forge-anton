import hashlib
import secrets

API_KEY_PREFIX = "wgr_"


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def generate_api_key() -> tuple[str, str, str]:
    raw = API_KEY_PREFIX + secrets.token_urlsafe(40)
    return raw, sha256(raw), raw[:8]


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
