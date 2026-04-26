"""Tests for entity dataclasses and OOP repositories."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.models import Base
from app.dto.documents import CreateDocumentRequest
from app.entities.document import Document
from app.entities.node import Node
from app.entities.edge import Edge
from app.entities.quiz import Quiz, Question
from app.repositories.document_repo import DocumentRepository
from app.repositories.node_repo import NodeRepository
from app.repositories.edge_repo import EdgeRepository
from app.repositories.quiz_repo import QuizRepository


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def doc_repo(db: Session):
    return DocumentRepository(db)


@pytest.fixture
def node_repo(db: Session):
    return NodeRepository(db)


@pytest.fixture
def edge_repo(db: Session):
    return EdgeRepository(db)


@pytest.fixture
def quiz_repo(db: Session):
    return QuizRepository(db)


class TestDocumentRepository:
    def test_create_and_get(self, doc_repo):
        from app.entities.document import Document
        doc = Document(title="Test Doc", source_path="/tmp/test.pdf")
        created = doc_repo.create_from_entity(doc)
        assert created.id is not None
        assert created.title == "Test Doc"
        fetched = doc_repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.title == created.title

    def test_create_from_dto(self, doc_repo):
        dto = CreateDocumentRequest(title="DTO Doc", file_path="/tmp/dto.pdf")
        created = doc_repo.create(dto)
        assert created.id is not None
        assert created.title == "DTO Doc"
        assert created.status == "pending"

    def test_update_status(self, doc_repo):
        dto = CreateDocumentRequest(title="Status Doc", file_path="/tmp/status.pdf")
        created = doc_repo.create(dto)
        updated = doc_repo.update_status(created.id, "completed")
        assert updated is not None
        assert updated.status == "completed"

    def test_delete(self, doc_repo):
        dto = CreateDocumentRequest(title="Del Doc", file_path="/tmp/del.pdf")
        created = doc_repo.create(dto)
        assert doc_repo.delete(created.id) is True
        assert doc_repo.get_by_id(created.id) is None

    def test_list_all(self, doc_repo):
        for i in range(3):
            doc_repo.create(CreateDocumentRequest(title=f"Doc{i}", file_path=f"/tmp/{i}.pdf"))
        docs = doc_repo.list_all(limit=10)
        assert len(docs) == 3


class TestNodeRepository:
    def test_create_and_get(self, node_repo):
        node = Node(doc_id=1, label="Concept A", summary="Summary A")
        created = node_repo.create(node)
        assert created.id is not None
        assert created.label == "Concept A"
        fetched = node_repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.label == "Concept A"

    def test_list_by_document(self, node_repo):
        for i in range(3):
            node_repo.create(Node(doc_id=1, label=f"Node{i}"))
        node_repo.create(Node(doc_id=2, label="Other doc"))
        nodes = node_repo.list_by_document(1)
        assert len(nodes) == 3

    def test_update(self, node_repo):
        created = node_repo.create(Node(doc_id=1, label="Old"))
        updated = node_repo.update(created.id, label="New")
        assert updated is not None
        assert updated.label == "New"

    def test_delete(self, node_repo):
        created = node_repo.create(Node(doc_id=1, label="ToDelete"))
        assert node_repo.delete(created.id) is True
        assert node_repo.get_by_id(created.id) is None


class TestEdgeRepository:
    def test_create_and_get(self, edge_repo):
        edge = Edge(source_node_id=1, target_node_id=2, doc_id=1, relation_type="relates_to")
        created = edge_repo.create(edge)
        assert created.id is not None
        assert created.relation_type == "relates_to"
        fetched = edge_repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.source_node_id == 1

    def test_list_by_document(self, edge_repo):
        for i in range(3):
            edge_repo.create(Edge(source_node_id=1, target_node_id=2, doc_id=1))
        edge_repo.create(Edge(source_node_id=1, target_node_id=2, doc_id=2))
        edges = edge_repo.list_by_document(1)
        assert len(edges) == 3

    def test_list_by_nodes(self, edge_repo):
        edge_repo.create(Edge(source_node_id=1, target_node_id=2, doc_id=1))
        edge_repo.create(Edge(source_node_id=1, target_node_id=2, doc_id=1))
        edge_repo.create(Edge(source_node_id=2, target_node_id=3, doc_id=1))
        edges = edge_repo.list_by_nodes(1, 2)
        assert len(edges) == 2

    def test_delete(self, edge_repo):
        created = edge_repo.create(Edge(source_node_id=1, target_node_id=2, doc_id=1))
        assert edge_repo.delete(created.id) is True
        assert edge_repo.get_by_id(created.id) is None


class TestQuizRepository:
    def test_create_and_get(self, quiz_repo):
        quiz = Quiz(doc_id=1, total_questions=1, questions=[
            Question(text="Q1", options=["A", "B"], correct_index=0),
        ])
        created = quiz_repo.create(quiz)
        assert created.id is not None
        assert created.total_questions == 1
        fetched = quiz_repo.get_by_id(created.id)
        assert fetched is not None
        assert len(fetched.questions) == 1

    def test_list_by_document(self, quiz_repo):
        for i in range(2):
            quiz_repo.create(Quiz(doc_id=1, total_questions=1))
        quiz_repo.create(Quiz(doc_id=2, total_questions=1))
        quizzes = quiz_repo.list_by_document(1)
        assert len(quizzes) == 2

    def test_delete(self, quiz_repo):
        created = quiz_repo.create(Quiz(doc_id=1, total_questions=1))
        assert quiz_repo.delete(created.id) is True
        assert quiz_repo.get_by_id(created.id) is None


class TestEntityDataclasses:
    def test_document_defaults(self):
        d = Document()
        assert d.id is None
        assert d.status == "pending"

    def test_node_defaults(self):
        n = Node()
        assert n.color == "#4ECDC4"
        assert n.doc_id == 0

    def test_edge_defaults(self):
        e = Edge()
        assert e.strength is None

    def test_quiz_defaults(self):
        q = Quiz()
        assert q.questions == []
        assert q.total_questions == 0

    def test_question_defaults(self):
        q = Question()
        assert q.options == []
        assert q.correct_index == 0
