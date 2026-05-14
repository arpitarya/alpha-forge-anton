"""Application-wide configuration loaded from environment variables."""

from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.env_loader import get_env_files, load_env_files

_LOADED_ENV_FILES = load_env_files()

# bcrypt(rounds=10) of "alphaforge-dev" — only valid in APP_ENV=development
_DEV_PASSWORD_HASH = "$2b$10$A0KihioA2iYqL64yVkz8beVxCnryP.4CkYPQUUgyJF7HW8GFwf8Zu"  # noqa: S105


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_files(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────
    app_name: str = "AlphaForge"
    app_env: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # ── Database ─────────────────────────────────
    database_url: str = "postgresql+asyncpg://alphaforge:alphaforge@localhost:5432/alphaforge"

    # ── Auth / JWT ───────────────────────────────
    jwt_secret_key: str = "change-me-in-production"  # noqa: S105
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    admin_username: str = "admin"
    # Defaults to bcrypt("alphaforge-dev") in dev; must be set explicitly in production.
    admin_password_hash: str = _DEV_PASSWORD_HASH

    # ── LLM Gateway (free multi-provider) ────────
    gemini_api_key: str = ""
    groq_api_key: str = ""
    huggingface_api_key: str = ""
    openrouter_api_key: str = ""
    ollama_base_url: str = "http://localhost:11434"

    # ── Vector / Memory ──────────────────────────
    embedding_model: str = "text-embedding-004"
    embedding_dimensions: int = 768
    memory_top_k: int = 5
    memory_max_age_days: int = 90

    # ── CORS ─────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000"]

    # ── Logging ──────────────────────────────────
    log_level: str = "INFO"
    log_dir: str = "logs"
    log_file: str = "alphaforge.log"
    log_max_bytes: int = 10_485_760  # 10 MB
    log_backup_count: int = 5

    @model_validator(mode="after")
    def _validate_secrets(self) -> "Settings":
        is_bcrypt = self.admin_password_hash.startswith(("$2b$", "$2a$"))

        if not is_bcrypt:
            if self.app_env != "development":
                raise ValueError(
                    "ADMIN_PASSWORD_HASH must be a valid bcrypt hash ($2b$...) in production"
                )
            # Dev: plaintext or blank value → silently use built-in default
            self.admin_password_hash = _DEV_PASSWORD_HASH
            return self

        if self.app_env != "development":
            if self.jwt_secret_key == "change-me-in-production":  # noqa: S105
                raise ValueError(
                    "JWT_SECRET_KEY must be changed from the default before running in production"
                )
            if self.admin_password_hash == _DEV_PASSWORD_HASH:
                raise ValueError("ADMIN_PASSWORD_HASH must be set to a secure value in production")
        return self


settings = Settings()
