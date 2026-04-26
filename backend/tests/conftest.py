"""Backend test fixtures — conftest.py

Provides shared fixtures for the entire test suite:
- test_db : transactional in-memory SQLite session
- client  : FastAPI TestClient
- ollama_mock : mock Ollama responses
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# ── PYTHONPATH setup ──────────────────────────────────────────────
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


# ── Fixtures ────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def test_db() -> Session:
    """Provide a transactional in-memory SQLite session.

    Tables are created before each test and dropped afterward.
    """
    from app.database.models import Base

    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    """Yield a FastAPI TestClient for end-to-end (no-db) route testing."""
    from app.main import create_app

    app = create_app()
    with TestClient(app) as tc:
        yield tc


@pytest.fixture
def ollama_mock():
    """Mock Ollama client with predictable responses."""
    from unittest.mock import AsyncMock, Mock

    mock = Mock()
    mock.generate = AsyncMock(
        return_value={
            "response": "Mocked summary text",
            "done": True,
            "total_duration": 1_000_000_000,
        }
    )
    mock.embed = AsyncMock(return_value={"embedding": [0.1] * 512})
    mock.health = AsyncMock(return_value={"status": "ok"})
    return mock
