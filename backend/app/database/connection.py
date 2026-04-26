"""Database connection manager."""
from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import get_settings

DEFAULT_DB_PATH = Path.home() / ".visual-learner" / "data.sqlite"
TEST_DB_URL = "sqlite:///:memory:"


def _default_db_url() -> str:
    try:
        settings = get_settings()
        return settings.DATABASE_URL
    except Exception:
        os.makedirs(DEFAULT_DB_PATH.parent, exist_ok=True)
        return f"sqlite:///{DEFAULT_DB_PATH}"


class DatabaseConnection:
    """Manages the SQLAlchemy engine and session lifecycle."""

    def __init__(self, database_url: str | None = None) -> None:
        self._database_url = database_url or _default_db_url()
        if self._database_url.startswith("sqlite:///"):
            db_path = Path(self._database_url.replace("sqlite:///", ""))
            db_path = db_path.expanduser()
            os.makedirs(db_path.parent, exist_ok=True)
        self._engine = self._create_engine()
        self._session_maker = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
            expire_on_commit=False,
        )

    def _create_engine(self):
        """Create SQLAlchemy engine with SQLite optimisations."""
        engine = create_engine(
            self._database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False,
        )

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine

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

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self._session_maker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_tables(self, base=None) -> None:
        """Create all tables registered with the declarative base."""
        if base is None:
            from app.database.models import Base
        else:
            Base = base
        Base.metadata.create_all(bind=self._engine)

    def drop_tables(self, base=None) -> None:
        """Drop all tables registered with the declarative base."""
        if base is None:
            from app.database.models import Base
        else:
            Base = base
        Base.metadata.drop_all(bind=self._engine)

    def health_check(self) -> dict:
        """Verify database connectivity and foreign key enforcement."""
        try:
            with self.session_scope() as session:
                result = session.execute(text("PRAGMA foreign_keys")).scalar()
            return {"status": "ok", "foreign_keys_enabled": bool(result)}
        except Exception as e:
            return {"status": "error", "error": str(e)}


def get_db() -> Generator[Session, None, None]:
    """Default dependency-compatible session generator for FastAPI."""
    conn = DatabaseConnection()
    yield from conn.get_session()
