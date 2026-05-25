"""Application-wide configuration loaded from environment variables."""

from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.env_loader import get_env_files, load_env_files

_LOADED_ENV_FILES = load_env_files()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_files(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────
    app_name: str = "AlphaForge Anton"
    app_env: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # ── Database ─────────────────────────────────
    database_url: str = "postgresql+asyncpg://alphaforge_anton:alphaforge_anton@localhost:5432/alphaforge_anton"

    # ── Auth / JWT — verify tokens issued by Wagner ──────────────
    jwt_secret_key: str = "change-me-in-production"  # noqa: S105
    jwt_algorithm: str = "HS256"

    # ── Wagner IAM service ───────────────────────
    wagner_url: str = "http://127.0.0.1:8001"

    # ── CORS ─────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000"]

    # ── Logging ──────────────────────────────────
    log_level: str = "INFO"
    log_dir: str = "logs"
    log_file: str = "alphaforge-anton.log"
    log_max_bytes: int = 10_485_760  # 10 MB
    log_backup_count: int = 5

    @model_validator(mode="after")
    def _validate_secrets(self) -> "Settings":
        if self.app_env != "development":
            if self.jwt_secret_key == "change-me-in-production":  # noqa: S105
                raise ValueError(
                    "JWT_SECRET_KEY must be changed from the default before running in production"
                )
        return self


settings = Settings()
