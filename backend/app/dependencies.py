"""
FastAPI Dependency Injection providers.

All route dependencies are resolved through this module. No globals, no
module-level state — only factory functions returning wired instances.

Usage in routers:
    from app.dependencies import get_doc_repo, ContainerDep

    @router.get("/")
    def list_docs(repo: DocumentRepository = Depends(get_doc_repo)):
        return repo.list_all()
"""
from __future__ import annotations

from typing import Annotated, Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db as _get_db
from app.di.container import Container, get_container
from app.repositories.document_repo import DocumentRepository
from app.repositories.edge_repo import EdgeRepository
from app.repositories.node_repo import NodeRepository
from app.repositories.quiz_repo import QuizRepository
from app.repositories.score_repo import ScoreRepository
from app.services.ollama_client import OllamaClient
from app.services.graph_service import GraphService
from app.services.quiz_service import QuizEngine


# ------------------------------------------------------------------
# DB session for FastAPI Depends()
# ------------------------------------------------------------------
get_db = _get_db  # Re-export for router usage if needed


# ------------------------------------------------------------------
# Container wired to the request DB session
# ------------------------------------------------------------------
def _get_wired_container(db: Session = Depends(get_db)) -> Container:
    """Return a Container with the current request's DB session bound."""
    return get_container().bind_session(db)


# Type alias for injection
ContainerDep = Annotated[Container, Depends(_get_wired_container)]


# ------------------------------------------------------------------
# Direct repository providers (syntactic sugar)
# ------------------------------------------------------------------
def get_doc_repo(container: ContainerDep) -> DocumentRepository:
    return container.document_repository


def get_node_repo(container: ContainerDep) -> NodeRepository:
    return container.node_repository


def get_quiz_repo(container: ContainerDep) -> QuizRepository:
    return container.quiz_repository


def get_score_repo(container: ContainerDep) -> ScoreRepository:
    return container.score_repository


# ------------------------------------------------------------------
# Service providers (syntactic sugar)
# ------------------------------------------------------------------
def get_graph_service(container: ContainerDep) -> GraphService:
    return container.graph_service


def get_quiz_service(container: ContainerDep) -> QuizEngine:
    return container.quiz_service


def get_ollama_client(container: ContainerDep) -> OllamaClient:
    return container.ollama_client
