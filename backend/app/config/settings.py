"""
Typed application configuration loaded from environment variables and .env files.

Uses pydantic-settings for validation, type coercion, and .env support.
Priority (highest → lowest):
  1. System environment variables
  2. .env file in project root (autodetected by pydantic-settings)
  3. Default values defined here
"""
from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


# Compute project root relative to this file: backend/app/config/settings.py → project root
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DB_PATH = Path.home() / ".visual-learner" / "data.sqlite"


class Settings(BaseSettings):
    """Application settings singleton."""

    # --- Ollama -----------------------------------------------------------
    OLLAMA_ENDPOINT: str = Field(default="https://ollama.com/v1", description="Ollama API endpoint URL")
    OLLAMA_API_KEY: str = Field(default="", description="Ollama API key (if required by proxy)")
    OLLAMA_MODEL: str = Field(default="llama3.1", description="Default model for generation tasks")

    # --- Database -----------------------------------------------------------
    DATABASE_URL: str = Field(
        default=f"sqlite:///{_DEFAULT_DB_PATH}",
        description="SQLAlchemy-compatible database URL",
    )

    # --- App ----------------------------------------------------------------
    LOG_LEVEL: str = Field(default="INFO", description="Python logging level")
    APP_VERSION: str = Field(default="0.1.0", description="Application version string")

    # --- Frontend overrides (via .env if needed) ----------------------------
    # VITE_* are read here only for backend awareness; Vite reads them directly.
    VITE_API_BASE_URL: str = Field(default="http://localhost:8000", description="Frontend API base URL")
    VITE_APP_VERSION: str = Field(default="0.1.0", description="Frontend version string")

    model_config = SettingsConfigDict(
        env_file=_PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # allow other env vars without raising
    )

    # ------------------------------------------------------------------
    @field_validator("LOG_LEVEL")
    @classmethod
    def _validate_log_level(cls, v: str) -> str:
        v_upper = v.upper()
        allowed = {"DEBUG", "INFO", "WARNING", "WARN", "ERROR", "CRITICAL", "FATAL"}
        if v_upper not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}, got {v!r}")
        return v_upper

    @field_validator("DATABASE_URL")
    @classmethod
    def _validate_database_url(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("DATABASE_URL cannot be empty")
        # Ensure sqlite path parent dirs exist eagerly
        if v.startswith("sqlite:///"):
            db_path = Path(v.replace("sqlite:///", ""))
            # Convert ~ to home
            db_path = db_path.expanduser()
            db_path.parent.mkdir(parents=True, exist_ok=True)
        return v

    # ------------------------------------------------------------------
    def configure_logging(self) -> None:
        """Apply LOG_LEVEL to the root logger."""
        level = getattr(logging, self.LOG_LEVEL, logging.INFO)
        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logger.debug(f"Logging configured at {self.LOG_LEVEL}")


@lru_cache()
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    return Settings()
