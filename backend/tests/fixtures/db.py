from typing import Generator

import pytest
from app.database.connection import DatabaseConnection
from app.database.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provide a transactional database session for tests.

    Tables are created before each test and dropped after.
    """
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session: Session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_connection():
    """Fresh DatabaseConnection per test (in-memory SQLite)."""
    conn = DatabaseConnection(database_url="sqlite:///:memory:")
    conn.create_tables()
    yield conn
    conn.drop_tables()
