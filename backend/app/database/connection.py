import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

DEFAULT_DB_PATH = Path.home() / ".visual-learner" / "data.sqlite"
TEST_DB_URL = "sqlite:///:memory:"


class DatabaseConnection:
    """Manages the SQLAlchemy engine and session lifecycle."""

    def __init__(self, database_url: str | None = None) -> None:
        if database_url is None:
            os.makedirs(DEFAULT_DB_PATH.parent, exist_ok=True)
            database_url = f"sqlite:///{DEFAULT_DB_PATH}"
        self._database_url = database_url
        self._engine = create_engine(
            self._database_url,
            connect_args={"check_same_thread": False},
        )
        self._session_maker = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
            expire_on_commit=False,
        )

    @property
    def engine(self):
        return self._engine

    def create_engine(self):
        """Return the SQLAlchemy engine (idempotent)."""
        return self._engine

    def get_session(self) -> Generator[Session, None, None]:
        """Yield a transactional session and ensure cleanup."""
        db: Session = self._session_maker()
        try:
            yield db
        finally:
            db.close()

    def create_tables(self, base) -> None:
        """Create all tables registered with the declarative base."""
        base.metadata.create_all(bind=self._engine)


def get_db() -> Generator[Session, None, None]:
    """Default dependency-compatible session generator for FastAPI."""
    conn = DatabaseConnection()
    yield from conn.get_session()
