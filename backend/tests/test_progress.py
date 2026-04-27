"""Tests for pipeline progress tracking (Issue #44)."""

import pytest
from app.dto.documents import DocumentState
from app.entities.job import Job
from app.repositories.job_repo import JobRepository
from app.routers.progress import default_progress_tracker, get_document_status
from app.services.state_machine import ProgressTracker


# ────────────────────────────────────────────────────────────────
# Unit: Job entity
# ────────────────────────────────────────────────────────────────
class TestJobEntity:
    def test_job_default_values(self) -> None:
        job = Job(doc_id=42)
        assert job.id is None
        assert job.doc_id == 42
        assert job.stage == "uploaded"
        assert job.progress == 0.0
        assert job.error_msg is None

    def test_job_custom_values(self) -> None:
        job = Job(
            id=1,
            doc_id=42,
            stage="reading",
            progress=0.5,
            error_msg="oops",
        )
        assert job.id == 1
        assert job.stage == "reading"
        assert job.progress == 0.5
        assert job.error_msg == "oops"


# ════════════════════════════════════════════════════════════════
# Integration: JobRepository against real DB session
# ════════════════════════════════════════════════════════════════
class TestJobRepository:
    def test_create_job(self, test_db) -> None:
        repo = JobRepository(test_db)
        job = repo.create(doc_id=7)
        assert job.id is not None
        assert job.doc_id == 7
        assert job.stage == "uploaded"
        assert job.progress == 0.0

    def test_get_by_doc_id(self, test_db) -> None:
        repo = JobRepository(test_db)
        created = repo.create(doc_id=99)
        fetched = repo.get_by_doc_id(99)
        assert fetched is not None
        assert fetched.id == created.id

    def test_get_by_doc_id__returns_none(self, test_db) -> None:
        repo = JobRepository(test_db)
        assert repo.get_by_doc_id(99999) is None

    def test_update_progress(self, test_db) -> None:
        repo = JobRepository(test_db)
        repo.create(doc_id=5)
        updated = repo.update_progress(doc_id=5, stage="reading", progress=0.3)
        assert updated.stage == "reading"
        assert updated.progress == 0.3

    def test_fail(self, test_db) -> None:
        repo = JobRepository(test_db)
        repo.create(doc_id=11)
        failed = repo.fail(doc_id=11, error_msg="PDF corrupted")
        assert failed.stage == "failed"
        assert failed.error_msg == "PDF corrupted"

    def test_delete(self, test_db) -> None:
        repo = JobRepository(test_db)
        repo.create(doc_id=88)
        assert repo.get_by_doc_id(88) is not None
        repo.delete(88)
        assert repo.get_by_doc_id(88) is None


# ════════════════════════════════════════════════════════════════
# Unit: default_progress_tracker helper
# ════════════════════════════════════════════════════════════════
class TestDefaultProgressTracker:
    def test_sets_state(self) -> None:
        tracker = default_progress_tracker(doc_id=42, to_state=DocumentState.READING)
        assert tracker.current_state == DocumentState.READING
        assert 42 in _trackers_cache()

    def test_keeps_stage_progress(self) -> None:
        tracker = default_progress_tracker(doc_id=43, to_state=DocumentState.READING, stage_progress=0.5)
        assert tracker.current_state == DocumentState.READING
        assert tracker.stage_progress == 0.5

    def test_overall_progress(self) -> None:
        tracker = default_progress_tracker(doc_id=44, to_state=DocumentState.UPLOADED)
        tracker.advance(DocumentState.READING)
        tracker.advance(DocumentState.PARSING)
        tracker.advance(DocumentState.ANALYZING)
        tracker.advance(DocumentState.GRAPH_BUILDING)
        tracker.advance(DocumentState.QUIZ_GENERATING)
        tracker.advance(DocumentState.COMPLETED)
        assert tracker.overall_progress == pytest.approx(1.0, rel=1e-6)


# ════════════════════════════════════════════════════════════════
# Unit: get_document_status helper (used by /documents/{id}/status)
# ════════════════════════════════════════════════════════════════
class TestGetDocumentStatus:
    def test_initial_status(self) -> None:
        status = get_document_status(1)
        assert status["document_id"] == 1
        assert status["stage"] == "uploaded"
        assert "Waiting" in status["stage_label"] or "uploaded" in status["stage_label"].lower()
        assert status["progress"] == 0.0
        assert status["error"] is None

    def test_reading_status(self) -> None:
        default_progress_tracker(2, DocumentState.READING, stage_progress=0.5)
        status = get_document_status(2)
        assert status["stage"] == "reading"
        assert "Reading PDF" in status["stage_label"]
        assert status["progress"] > 0
        assert status["error"] is None

    def test_failed_status(self) -> None:
        tracker = default_progress_tracker(3, DocumentState.READING)
        tracker.fail("Ollama timeout", stage_progress=0.3)
        status = get_document_status(3)
        assert status["stage"] == "failed"
        assert status["error"] == "Ollama timeout"
        assert status["progress"] > 0


# ─── tiny helper ────────────────────────────────────────────────

def _trackers_cache() -> dict:
    from app.routers.progress import _trackers
    return _trackers
