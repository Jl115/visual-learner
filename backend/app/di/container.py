"""
Lazy-initialising Dependency Injection Container.

* No module-level state
* Every dependency is injected via __init__
* Services / repos are created on first access (lazy)
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from app.config import Settings, get_settings
from app.repositories.document_repo import DocumentRepository
from app.repositories.edge_repo import EdgeRepository
from app.repositories.job_repo import JobRepository
from app.repositories.node_repo import NodeRepository
from app.repositories.quiz_repo import QuizRepository
from app.repositories.score_repo import ScoreRepository
from app.services.file_reader_service import FileReaderService
from app.services.graph_service import GraphBuilder, GraphService
from app.services.nlp_pipeline import NLPPipeline
from app.services.ollama_client import OllamaClient
from app.services.quiz_service import QuizEngine

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class Container:
    """Production DI container. No globals, all lazy."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._db: Session | None = None  # injected per-request
        self._ollama: OllamaClient | None = None
        self._nlp: NLPPipeline | None = None
        self._graph_builder: GraphBuilder | None = None
        self._graph_service: GraphService | None = None
        self._quiz_engine: QuizEngine | None = None
        self._file_reader: FileReaderService | None = None
        self._document_repo: DocumentRepository | None = None
        self._edge_repo: EdgeRepository | None = None
        self._job_repo: JobRepository | None = None
        self._node_repo: NodeRepository | None = None
        self._quiz_repo: QuizRepository | None = None
        self._score_repo: ScoreRepository | None = None

    # ------------------------------------------------------------------
    # Settings
    # ------------------------------------------------------------------
    @property
    def settings(self) -> Settings:
        return self._settings

    @property
    def db_url(self) -> str:
        return self._settings.DATABASE_URL

    # ------------------------------------------------------------------
    # Low-level clients (stateless, safe to cache)
    # ------------------------------------------------------------------
    @property
    def ollama_client(self) -> OllamaClient:
        if self._ollama is None:
            self._ollama = OllamaClient(
                base_url=self._settings.OLLAMA_ENDPOINT,
                api_key=self._settings.OLLAMA_API_KEY,
                model=self._settings.OLLAMA_MODEL,
            )
        return self._ollama

    @property
    def nlp_pipeline(self) -> NLPPipeline:
        if self._nlp is None:
            self._nlp = NLPPipeline()
        return self._nlp

    @property
    def graph_builder(self) -> GraphBuilder:
        if self._graph_builder is None:
            self._graph_builder = GraphBuilder()
        return self._graph_builder

    # ------------------------------------------------------------------
    # Services — injected with repos + clients
    # ------------------------------------------------------------------
    @property
    def graph_service(self) -> GraphService:
        if self._graph_service is None:
            self._graph_service = GraphService(
                repo=self.node_repository,
                ollama=self.ollama_client,
                builder=self.graph_builder,
                edge_repo=self.edge_repository,
            )
        return self._graph_service

    @property
    def quiz_service(self) -> QuizEngine:
        if self._quiz_engine is None:
            self._quiz_engine = QuizEngine(self.ollama_client)
        return self._quiz_engine

    @property
    def file_reader_service(self) -> FileReaderService:
        if self._file_reader is None:
            self._file_reader = FileReaderService()
        return self._file_reader

    # ------------------------------------------------------------------
    # Repositories — take db.Session injected per-request
    # ------------------------------------------------------------------
    @property
    def document_repository(self) -> DocumentRepository:
        if self._document_repo is None:
            self._document_repo = DocumentRepository(self._resolve_db())
        return self._document_repo

    @property
    def node_repository(self) -> NodeRepository:
        if self._node_repo is None:
            self._node_repo = NodeRepository(self._resolve_db())
        return self._node_repo

    @property
    def edge_repository(self) -> EdgeRepository:
        if self._edge_repo is None:
            self._edge_repo = EdgeRepository(self._resolve_db())
        return self._edge_repo

    @property
    def job_repository(self) -> JobRepository:
        if self._job_repo is None:
            self._job_repo = JobRepository(self._resolve_db())
        return self._job_repo

    @property
    def quiz_repository(self) -> QuizRepository:
        if self._quiz_repo is None:
            self._quiz_repo = QuizRepository(self._resolve_db())
        return self._quiz_repo

    @property
    def score_repository(self) -> ScoreRepository:
        if self._score_repo is None:
            self._score_repo = ScoreRepository(self._resolve_db())
        return self._score_repo

    # ------------------------------------------------------------------
    # request-scoped helpers
    # ------------------------------------------------------------------
    def _resolve_db(self) -> Session:
        if self._db is None:
            raise RuntimeError(
                "Database session must be bound before accessing repositories. "
                "Use `container.bind_session(db)` in the request lifecycle."
            )
        return self._db

    def bind_session(self, db: Session) -> Container:
        """Attach a request-scoped DB session (returns self for chaining)."""
        self._db = db
        return self

    def release_session(self) -> Container:
        """Release the current DB session — useful between requests."""
        self._db = None
        self._document_repo = None
        self._edge_repo = None
        self._job_repo = None
        self._node_repo = None
        self._quiz_repo = None
        self._score_repo = None
        self._graph_service = None
        self._quiz_engine = None
        self._file_reader = None
        return self


# ------------------------------------------------------------------
# Application-scoped container factory
# ------------------------------------------------------------------
@lru_cache(maxsize=1)
def _get_cached_settings() -> Settings:
    return get_settings()


def get_container(settings: Settings | None = None) -> Container:
    """Return a fresh Container (settings reused from cache for speed)."""
    return Container(settings or _get_cached_settings())
