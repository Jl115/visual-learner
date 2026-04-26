import os
from pathlib import Path
from unittest.mock import patch

import pytest


class TestSettingsDefaults:
    def test_default_fields(self):
        from app.config.settings import Settings

        s = Settings()
        assert s.OLLAMA_ENDPOINT == "https://ollama.com/v1"
        assert s.OLLAMA_API_KEY == ""
        assert s.OLLAMA_MODEL == "llama3.1"
        assert s.LOG_LEVEL == "INFO"
        assert s.APP_VERSION == "0.1.0"
        assert s.VITE_API_BASE_URL == "http://localhost:8000"
        assert s.DATABASE_URL.startswith("sqlite:///")

    def test_log_level_validation(self):
        from app.config.settings import Settings

        with pytest.raises(ValueError):
            Settings(LOG_LEVEL="INVALID")

    def test_log_level_normalization(self):
        from app.config.settings import Settings

        s = Settings(LOG_LEVEL="debug")
        assert s.LOG_LEVEL == "DEBUG"

    def test_database_url_ensures_dir(self, tmp_path: Path):
        from app.config.settings import Settings

        db_path = tmp_path / "sub" / "test.db"
        s = Settings(DATABASE_URL=f"sqlite:///{db_path}")
        assert db_path.parent.exists()

    def test_empty_database_url_raises(self):
        from app.config.settings import Settings

        with pytest.raises(ValueError):
            Settings(DATABASE_URL="   ")


class TestSettingsEnvOverride:
    def test_env_overrides_defaults(self):
        from app.config.settings import Settings

        env = {
            "OLLAMA_ENDPOINT": "http://localhost:11434",
            "OLLAMA_API_KEY": "secret",
            "OLLAMA_MODEL": "mistral",
            "LOG_LEVEL": "DEBUG",
            "APP_VERSION": "0.2.0",
        }
        with patch.dict(os.environ, env, clear=False):
            s = Settings()
            assert s.OLLAMA_ENDPOINT == "http://localhost:11434"
            assert s.OLLAMA_API_KEY == "secret"
            assert s.OLLAMA_MODEL == "mistral"
            assert s.LOG_LEVEL == "DEBUG"
            assert s.APP_VERSION == "0.2.0"


class TestGetSettingsCached:
    def test_singleton(self):
        from app.config.settings import get_settings

        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2


class TestSettingsConfigureLogging:
    def test_configure_logging(self):
        import logging
        from app.config.settings import Settings

        root = logging.getLogger()
        root.handlers.clear()
        s = Settings(LOG_LEVEL="ERROR")
        s.configure_logging()
        assert root.level == logging.ERROR
