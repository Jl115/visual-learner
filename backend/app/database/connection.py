"""Database connection manager for SQLite + SQLAlchemy."""
import os
from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from backend.app.database.models import Base


class DatabaseConnection:
    """Manages SQLite database engine and sessions."""

    def __init__(self, database_url: str | None = None) -> None:
        if database_url is None:
            # Default: store in user's home directory
            data_dir = Path.home() / ".visual-learner"
            data_dir.mkdir(parents=True, exist_ok=True)
            database_url = f"sqlite:///{data_dir}/data.sqlite"

        self.database_url = database_url
        self._engine = self._create_engine()
        self._sessionmaker = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._engine,
        )

    def _create_engine(self):
        """Create SQLAlchemy engine with SQLite optimisations."""
        connect_args = {"check_same_thread": False}
        engine = create_engine(
            self.database_url,
            connect_args=connect_args,
            poolclass=StaticPool,
            echo=False,
        )

        # Enable foreign key support for SQLite
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        return engine

    def create_tables(self) -> None:
        """Create all tables if they don't exist."""
        Base.metadata.create_all(bind=self._engine)

    def drop_tables(self) -> None:
        """Drop all tables (useful for testing)."""
        Base.metadata.drop_all(bind=self._engine)

    def get_session(self) -> Session:
        """Get a new session. Caller is responsible for commit/close."""
        return self._sessionmaker()

    @contextmanager
    def session_scope(self):
        """Context manager for transactional sessions."""
        session = self._sessionmaker()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def health_check(self) -> dict:
        """Verify the database is reachable."""
        try:
            from sqlalchemy import text
            with self.session_scope() as session:
                result = session.execute(text("PRAGMA foreign_keys")).scalar()
            return {"status": "ok", "foreign_keys": bool(result)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    @property
    def engine(self):
        return self._engine
