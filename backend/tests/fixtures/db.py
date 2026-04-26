"""Test fixtures for database + API testing."""
import pytest
from fastapi.testclient import TestClient

from backend.app.config.settings import Settings
from backend.app.database.connection import DatabaseConnection
from backend.app.database.models import Base


@pytest.fixture(scope="session")
def settings():
    """Settings fixture with test overrides."""
    return Settings(DATABASE_URL="sqlite:///:memory:")


@pytest.fixture(scope="function")
def db_connection(settings):
    """Fresh database connection per test (in-memory SQLite)."""
    conn = DatabaseConnection(database_url=settings.DATABASE_URL)
    conn.create_tables()
    yield conn
    conn.drop_tables()


@pytest.fixture(scope="function")
def db_session(db_connection):
    """Transactional test session with automatic rollback."""
    with db_connection.session_scope() as session:
        yield session


@pytest.fixture(scope="function")
def client(db_connection):
    """FastAPI TestClient with test DB wired in."""
    # Import here to ensure models are registered
    from backend.app.main import create_app
    
    app = create_app(db_connection=db_connection)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def _reset_settings_singleton(monkeypatch):
    """Reset Settings singleton between tests."""
    import backend.app.config.settings as _settings_module
    _settings_module._settings = None
