"""Environment configuration using pydantic-settings."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Ollama
    OLLAMA_ENDPOINT: str = "https://ollama.com/v1"
    OLLAMA_API_KEY: str = ""
    OLLAMA_MODEL: str = "llama3.1"

    # Database
    DATABASE_URL: str | None = None

    # Logging
    LOG_LEVEL: str = "INFO"

    # App
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    @property
    def resolved_database_url(self) -> str:
        """Return database URL with default fallback."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        data_dir = Path.home() / ".visual-learner"
        data_dir.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{data_dir}/data.sqlite"


# Global singleton — instantiated by DI container
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create Settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
