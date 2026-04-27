"""Job repository — SQLAlchemy backed."""

from __future__ import annotations

from typing import Optional

from app.database.models import JobModel
from app.entities.job import Job
from sqlalchemy.orm import Session


class JobRepository:
    """Repository for tracking document processing jobs (pipeline status)."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # ── CRUD ──────────────────────────────────────────────────────────

    def create(self, doc_id: int) -> Job:
        """Create a fresh job for a document."""
        model = JobModel(doc_id=doc_id)
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return self._to_domain(model)

    def get_by_doc_id(self, doc_id: int) -> Optional[Job]:
        """Fetch the latest job for a document."""
        model = (
            self._session.query(JobModel)
            .filter(JobModel.doc_id == doc_id)
            .order_by(JobModel.updated_at.desc())
            .first()
        )
        return self._to_domain(model) if model else None

    def update_progress(self, doc_id: int, stage: str, progress: float) -> Job:
        """Update the most recent job for a document."""
        model = (
            self._session.query(JobModel)
            .filter(JobModel.doc_id == doc_id)
            .order_by(JobModel.updated_at.desc())
            .first()
        )
        if model:
            model.stage = stage
            model.progress = progress
            self._session.flush()
            return self._to_domain(model)
        # If no job exists, create one
        return self.create_with_status(doc_id, stage, progress)

    def fail(self, doc_id: int, error_msg: str) -> Job:
        """Mark the most recent job as failed."""
        model = (
            self._session.query(JobModel)
            .filter(JobModel.doc_id == doc_id)
            .order_by(JobModel.updated_at.desc())
            .first()
        )
        if model:
            model.stage = "failed"
            model.error_msg = error_msg
            self._session.flush()
            return self._to_domain(model)
        raise RuntimeError(f"No job found for doc_id={doc_id} to mark as failed")

    def delete(self, doc_id: int) -> None:
        """Remove all jobs for a document."""
        self._session.query(JobModel).filter(JobModel.doc_id == doc_id).delete()
        self._session.flush()

    # ── helpers ─────────────────────────────────────────────────────

    def create_with_status(self, doc_id: int, stage: str, progress: float) -> Job:
        """Create or overwrite the job for a document with given stage/progress."""
        model = JobModel(doc_id=doc_id, stage=stage, progress=progress)
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: JobModel) -> Job:
        return Job(
            id=model.id,
            doc_id=model.doc_id,
            stage=model.stage,
            progress=model.progress,
            error_msg=model.error_msg,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
