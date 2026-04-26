"""Test DI Container with mock repository doubles."""
from __future__ import annotations

import pytest
from app.di.container import Container, get_container
from app.config import Settings
from app.entities.document import Document
from app.entities.node import Node
from app.entities.quiz import Quiz, Question


# ------------------------------------------------------------------
# MockRepository base class
# ------------------------------------------------------------------
class MockDocumentRepository:
    """In-memory double for DocumentRepository."""

    def __init__(self, db=None):
        self._items: list[dict] = []

    def create(self, document: Document) -> Document:
        self._items.append(document)
        return document

    def list_all(self, limit=50, offset=0) -> list[Document]:
        return self._items[offset : offset + limit]

    def get_by_id(self, doc_id: int) -> Document | None:
        return None

    def list_by_status(self, status: str, limit=50, offset=0) -> list[Document]:
        return []

    def update_status(self, doc_id: int, status: str, error_msg=None) -> Document | None:
        return None

    def delete(self, doc_id: int) -> bool:
        return False


class MockNodeRepository:
    """In-memory double for NodeRepository."""

    def __init__(self, db=None):
        self._items: list[Node] = []

    def create(self, node: Node) -> Node:
        self._items.append(node)
        return node

    def list_by_document(self, doc_id: int, limit=200, offset=0) -> list[Node]:
        return []

    def get_by_id(self, node_id: int) -> Node | None:
        return None

    def list_all(self, limit=50, offset=0) -> list[Node]:
        return self._items[offset : offset + limit]

    def update(self, node_id: int, **kwargs) -> Node | None:
        return None

    def delete(self, node_id: int) -> bool:
        return False


class MockQuizRepository:
    """In-memory double for QuizRepository."""

    def __init__(self, db=None):
        self._items: list[Quiz] = []

    def create(self, quiz: Quiz) -> Quiz:
        self._items.append(quiz)
        return quiz

    def list_by_document(self, doc_id: int, limit=50, offset=0) -> list[Quiz]:
        return []

    def get_by_id(self, quiz_id: int) -> Quiz | None:
        return None

    def list_all(self, limit=50, offset=0) -> list[Quiz]:
        return self._items[offset : offset + limit]

    def delete(self, quiz_id: int) -> bool:
        return False


# ------------------------------------------------------------------
# DI tests
# ------------------------------------------------------------------
class TestDIContainer:
    def test_container_requires_db_for_repos(self):
        container = Container()
        with pytest.raises(RuntimeError, match="Database session must be bound"):
            _ = container.document_repository

    def test_container_lazy_ollama_client(self):
        container = Container()
        ollama = container.ollama_client
        assert ollama is not None
        # verify cached
        assert container.ollama_client is ollama

    def test_container_lazy_nlp_pipeline(self):
        container = Container()
        nlp = container.nlp_pipeline
        assert nlp is not None
        assert container.nlp_pipeline is nlp

    def test_container_bind_release_cycle(self):
        container = Container()
        assert container._db is None

        # Simulate a DB session binding (use None for unit test)
        container.bind_session(None)
        assert container._db is None  # it is None, but logic won't fail now because we override

        # Directly patch repos for testing
        container._document_repo = MockDocumentRepository()
        container._node_repo = MockNodeRepository()
        container._quiz_repo = MockQuizRepository()

        doc = container.document_repository
        assert isinstance(doc, MockDocumentRepository)

        container.release_session()
        assert container._document_repo is None
        assert container._node_repo is None

    def test_get_container_returns_fresh_instance(self):
        c1 = get_container()
        c2 = get_container()
        assert c1 is not c2
        assert isinstance(c1, Container)


class TestGraphServiceWithMocks:
    def test_graph_service_with_node_repo(self):
        from app.services.graph_service import GraphService, GraphBuilder
        from app.services.ollama_client import OllamaClient

        # Build bare mock dependencies
        ollama = OllamaClient(base_url="http://test")
        repo = MockNodeRepository()
        builder = GraphBuilder()

        service = GraphService(repo=repo, ollama=ollama, builder=builder)
        assert service.repo is repo
        assert service.ollama is ollama
        nodes, edges = service.generate_graph("dummy text")
        assert nodes == []
        assert edges == []

    def test_graph_service_build_graph_returns_nx(self):
        import networkx as nx
        from app.services.graph_service import GraphService, GraphBuilder
        from app.services.ollama_client import OllamaClient

        service = GraphService(
            repo=MockNodeRepository(),
            ollama=OllamaClient(base_url="http://test"),
            builder=GraphBuilder(),
        )
        themes = [
            {"label": "A", "summary": "alpha", "weight": 1.0, "similarities": {"B": 0.8}},
            {"label": "B", "summary": "beta", "weight": 0.5, "similarities": {"A": 0.8}},
        ]
        graph = service.build_graph("doc-1", themes)
        assert isinstance(graph, nx.Graph)
        assert "A" in graph.nodes
        assert "B" in graph.nodes
        assert graph.has_edge("A", "B")


class TestQuizServiceWithMocks:
    def test_quiz_service_uses_ollama(self):
        from app.services.quiz_service import QuizEngine
        from app.services.ollama_client import OllamaClient

        ollama = OllamaClient(base_url="http://test")
        engine = QuizEngine(ollama)
        # Just verify wiring — actual async generation is stubbed
        assert engine.ollama is ollama
