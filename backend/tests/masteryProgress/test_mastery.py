"""Tests for the mastery service and repository."""

import pytest
from app.database.connection import DatabaseConnection
from app.database.models import Base, NodeModel, QuizModel, QuizAttemptModel
from app.entities.user_node_state import UserNodeState
from app.repositories.user_node_state_repo import UserNodeStateRepository
from app.services.mastery_service import MasteryService


@pytest.fixture
def in_memory_db():
    """Return a fresh in-memory SQLite database with all tables."""
    conn = DatabaseConnection("sqlite:///:memory:")
    Base.metadata.create_all(bind=conn.engine)
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(bind=conn.engine)
    db = SessionLocal()
    yield db
    db.rollback()
    db.close()


@pytest.fixture
def seeded_node(in_memory_db):
    """Seed a single document + node and return the node id."""
    db = in_memory_db
    from app.database.models import DocumentModel
    doc = DocumentModel(title="Test doc", source_path="/tmp/test.pdf")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    node = NodeModel(doc_id=doc.id, label="Sample node", color="#4ECDC4")
    db.add(node)
    db.commit()
    db.refresh(node)
    return node.id


# ------------------------------------------------------------------
# Repository tests
# ------------------------------------------------------------------

class TestUserNodeStateRepository:
    def test_create(self, in_memory_db, seeded_node):
        repo = UserNodeStateRepository(in_memory_db)
        state = repo.create(UserNodeState(node_id=seeded_node, state="new", review_count=0, id=None, last_reviewed=None, created_at=None))
        assert state.id is not None
        assert state.node_id == seeded_node
        assert state.state == "new"

    def test_get_by_node_id(self, in_memory_db, seeded_node):
        repo = UserNodeStateRepository(in_memory_db)
        state = repo.create(UserNodeState(node_id=seeded_node, state="reviewing", review_count=1))
        fetched = repo.get_by_node_id(seeded_node)
        assert fetched is not None
        assert fetched.state == "reviewing"

    def test_update_or_create__creates(self, in_memory_db, seeded_node):
        repo = UserNodeStateRepository(in_memory_db)
        state = repo.update_or_create(seeded_node, state="reviewing")
        assert state.state == "reviewing"
        assert repo.get_by_node_id(seeded_node).state == "reviewing"

    def test_update_or_create__updates(self, in_memory_db, seeded_node):
        repo = UserNodeStateRepository(in_memory_db)
        repo.update_or_create(seeded_node, state="reviewing", review_count=1)
        updated = repo.update_or_create(seeded_node, state="learned", review_count=2)
        assert updated.state == "learned"

    def test_document_stats(self, in_memory_db, seeded_node):
        repo = UserNodeStateRepository(in_memory_db)
        repo.update_or_create(seeded_node, state="reviewing", review_count=1)
        stats = repo.get_document_stats(1)
        assert stats["reviewing"] == 1
        assert stats["new"] == 0
        assert stats["learned"] == 0


# ------------------------------------------------------------------
# Service tests
# ------------------------------------------------------------------

class TestMasteryService:
    def test_init_node(self, in_memory_db, seeded_node):
        service = MasteryService(in_memory_db, UserNodeStateRepository(in_memory_db))
        state = service.init_node(seeded_node)
        assert state.state == "new"
        assert state.review_count == 0

    def test_init_node__idempotent(self, in_memory_db, seeded_node):
        service = MasteryService(in_memory_db, UserNodeStateRepository(in_memory_db))
        service.init_node(seeded_node)
        state2 = service.init_node(seeded_node)
        assert state2.state == "new"
        # Still should be the same record
        all_states = UserNodeStateRepository(in_memory_db).list_all()
        assert len(all_states) == 1

    def test_update_state(self, in_memory_db, seeded_node):
        service = MasteryService(in_memory_db, UserNodeStateRepository(in_memory_db))
        state = service.update_state(seeded_node, "learned")
        assert state.state == "learned"

    def test_record_attempt__promotes_to_reviewing(self, in_memory_db, seeded_node):
        service = MasteryService(in_memory_db, UserNodeStateRepository(in_memory_db))
        state = service.record_attempt(seeded_node, score=50, total=100)
        assert state.state == "reviewing"
        assert state.review_count == 1

    def test_record_attempt__does_not_promote_to_learned_with_single_attempt(self, in_memory_db, seeded_node):
        service = MasteryService(in_memory_db, UserNodeStateRepository(in_memory_db))
        state = service.record_attempt(seeded_node, score=90, total=100)
        # Still reviewing because only 1 attempt
        assert state.state == "reviewing"

    def test_reset_node(self, in_memory_db, seeded_node):
        service = MasteryService(in_memory_db, UserNodeStateRepository(in_memory_db))
        service.update_state(seeded_node, "learned")
        reset = service.reset_node(seeded_node)
        assert reset.state == "new"
        assert reset.review_count == 0

    def test_get_stats(self, in_memory_db, seeded_node):
        service = MasteryService(in_memory_db, UserNodeStateRepository(in_memory_db))
        service.update_state(seeded_node, "learned")
        stats = service.get_stats(1)
        assert stats["learned"] == 1
        assert stats["reviewing"] == 0


# ------------------------------------------------------------------
# Auto-promotion tests (learned threshold)
# ------------------------------------------------------------------

class TestLearnedAutoPromotion:
    def test_auto_promote_to_learned_after_two_high_attempts(self, in_memory_db, seeded_node):
        db = in_memory_db
        # Need a quiz + 2 attempts to simulate promotion
        quiz = QuizModel(doc_id=1, node_id=seeded_node, total_questions=5)
        db.add(quiz)
        db.commit()
        db.refresh(quiz)

        # Seed two high-scoring attempts
        for _ in range(2):
            attempt = QuizAttemptModel(quiz_id=quiz.id, score=5, total=5)
            db.add(attempt)
        db.commit()

        service = MasteryService(db, UserNodeStateRepository(db))
        # First attempt → reviewing
        state1 = service.record_attempt(seeded_node, score=5, total=5)
        # Second attempt → should promote to learned (avg=100%, attempts=2)
        state2 = service.record_attempt(seeded_node, score=5, total=5)
        assert state2.state == "learned"
