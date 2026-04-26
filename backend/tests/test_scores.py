"""Tests for score persistence, repository, and service."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.models import Base, DocumentModel, QuizModel, ScoreModel
from app.entities.score import Score
from app.repositories.score_repo import ScoreRepository
from app.services.score_service import ScoreService


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
def score_repo(db: Session):
    return ScoreRepository(db)


@pytest.fixture
def seeded_db(db: Session):
    """Seed a doc + quiz + scores for aggregation tests."""
    # Create document
    doc = DocumentModel(title="Test Doc", path="/tmp/t.pdf")
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Create quiz
    quiz = QuizModel(doc_id=doc.id, total_questions=3)
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    # Create scores — two attempts
    s1 = ScoreModel(document_id=doc.id, quiz_id=quiz.id, correct_count=2, total_count=3)
    s2 = ScoreModel(document_id=doc.id, quiz_id=quiz.id, correct_count=3, total_count=3)
    db.add_all([s1, s2])
    db.commit()

    return db, doc.id, quiz.id


# ──────────────────────────────────────
# Entity
# ──────────────────────────────────────
class TestScoreEntity:
    def test_score_defaults(self):
        s = Score(doc_id=1, quiz_id=2, correct_count=1, total_count=5)
        assert s.id is None
        assert s.correct_count == 1
        assert s.total_count == 5


# ──────────────────────────────────────
# Repository CRUD
# ──────────────────────────────────────
class TestScoreRepositoryCRUD:
    def test_create(self, score_repo):
        s = Score(doc_id=1, quiz_id=2, correct_count=2, total_count=3)
        created = score_repo.create(s)
        assert created.id is not None
        assert created.correct_count == 2
        assert created.total_count == 3

    def test_get_by_id(self, score_repo, seeded_db):
        db, doc_id, quiz_id = seeded_db
        s = score_repo.list_by_document(doc_id)[0]
        fetched = score_repo.get_by_id(s.id)
        assert fetched is not None
        assert fetched.doc_id == doc_id

    def test_list_by_document(self, score_repo, seeded_db):
        db, doc_id, quiz_id = seeded_db
        scores = score_repo.list_by_document(doc_id)
        assert len(scores) == 2

    def test_list_all(self, score_repo, seeded_db):
        db, doc_id, quiz_id = seeded_db
        scores = score_repo.list_all()
        assert len(scores) == 2

    def test_delete(self, score_repo, seeded_db):
        db, doc_id, quiz_id = seeded_db
        s = score_repo.list_by_document(doc_id)[0]
        assert score_repo.delete(s.id) is True
        assert score_repo.get_by_id(s.id) is None


# ──────────────────────────────────────
# Repository Aggregation
# ──────────────────────────────────────
class TestScoreRepositoryAggregation:
    def test_get_document_stats(self, score_repo, seeded_db):
        db, doc_id, quiz_id = seeded_db
        stats = score_repo.get_document_stats(doc_id)
        assert stats["doc_id"] == doc_id
        assert stats["total_correct"] == 5  # 2 + 3
        assert stats["total_possible"] == 6  # 3 + 3
        assert stats["attempt_count"] == 2

    def test_get_all_document_stats(self, score_repo, seeded_db):
        db, doc_id, quiz_id = seeded_db
        stats = score_repo.get_all_document_stats()
        assert len(stats) == 1
        row = stats[0]
        assert row["doc_id"] == doc_id
        assert row["doc_title"] == "Test Doc"
        assert row["total_correct"] == 5
        assert "accuracy" in row
        assert "last_attempt" in row

    def test_get_recent_scores(self, score_repo, seeded_db):
        db, doc_id, quiz_id = seeded_db
        recent = score_repo.get_recent_scores(limit=10)
        assert len(recent) == 2
        assert recent[0]["doc_title"] == "Test Doc"
        assert "timestamp" in recent[0]

    def test_get_document_stats_empty(self, score_repo):
        stats = score_repo.get_document_stats(999)
        assert stats["total_correct"] == 0
        assert stats["attempt_count"] == 0

    def test_get_all_document_stats_empty(self, score_repo):
        stats = score_repo.get_all_document_stats()
        assert stats == []


# ──────────────────────────────────────
# Service layer
# ──────────────────────────────────────
class TestScoreService:
    def test_record(self, score_repo, seeded_db):
        db, doc_id, quiz_id = seeded_db
        svc = ScoreService(score_repo)
        new = svc.record(doc_id=doc_id, quiz_id=quiz_id, correct=1, total=5)
        assert new.correct_count == 1
        assert new.total_count == 5

    def test_get_document_stats(self, score_repo, seeded_db):
        svc = ScoreService(score_repo)
        stats = svc.get_document_stats(seeded_db[1])
        assert stats["attempt_count"] == 2

    def test_get_all_document_stats(self, score_repo, seeded_db):
        svc = ScoreService(score_repo)
        stats = svc.get_all_document_stats()
        assert len(stats) == 1

    def test_get_recent(self, score_repo, seeded_db):
        svc = ScoreService(score_repo)
        recent = svc.get_recent(limit=10)
        assert len(recent) == 2
