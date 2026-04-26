"""Score / quiz result repository."""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import ScoreModel
from app.entities.score import Score
from app.repositories.base_repository import BaseRepository


class ScoreRepository(BaseRepository):
    """CRUD + aggregation for Score entities."""

    _model_cls = ScoreModel

    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_domain(self, model: ScoreModel) -> Score:
        return Score(
            id=model.id,
            doc_id=model.document_id,
            quiz_id=model.quiz_id,
            correct_count=model.correct_count,
            total_count=model.total_count,
            timestamp=model.timestamp,
        )

    def get_by_id(self, score_id: int) -> Optional[Score]:
        model = self._db.query(ScoreModel).filter_by(id=score_id).first()
        return self._to_domain(model) if model else None

    def list_by_document(self, doc_id: int, limit: int = 50, offset: int = 0) -> List[Score]:
        rows = (
            self._db.query(ScoreModel)
            .filter_by(document_id=doc_id)
            .order_by(ScoreModel.timestamp.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def list_all(self, limit: int = 200, offset: int = 0) -> List[Score]:
        rows = (
            self._db.query(ScoreModel)
            .order_by(ScoreModel.timestamp.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def create(self, domain: Score) -> Score:
        model = ScoreModel(
            document_id=domain.doc_id,
            quiz_id=domain.quiz_id,
            correct_count=domain.correct_count,
            total_count=domain.total_count,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def delete(self, score_id: int) -> bool:
        model = self._db.query(ScoreModel).filter_by(id=score_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True

    # ------------------------------------------------------------------
    # Aggregation helpers (for bar charts + badges)
    # ------------------------------------------------------------------

    def get_document_stats(self, doc_id: int) -> Dict[str, Any]:
        """Total correct, total possible, avg per attempt for a single document."""
        total_correct = (
            self._db.query(func.sum(ScoreModel.correct_count))
            .filter_by(document_id=doc_id)
            .scalar()
            or 0
        )
        total_possible = (
            self._db.query(func.sum(ScoreModel.total_count))
            .filter_by(document_id=doc_id)
            .scalar()
            or 1  # avoid div-by-zero; handled below
        )
        attempt_count = (
            self._db.query(func.count(ScoreModel.id))
            .filter_by(document_id=doc_id)
            .scalar()
            or 0
        )
        return {
            "doc_id": doc_id,
            "total_correct": int(total_correct),
            "total_possible": int(total_possible),
            "attempt_count": int(attempt_count),
            "accuracy": round(total_correct / total_possible, 4) if total_possible else 0.0,
        }

    def get_all_document_stats(self) -> List[Dict[str, Any]]:
        """Aggregated stats for every document that has scores."""
        from app.database.models import DocumentModel
        rows = (
            self._db.query(
                DocumentModel.id.label("doc_id"),
                DocumentModel.title.label("doc_title"),
                func.sum(ScoreModel.correct_count).label("total_correct"),
                func.sum(ScoreModel.total_count).label("total_possible"),
                func.count(ScoreModel.id).label("attempt_count"),
                func.max(ScoreModel.timestamp).label("last_attempt"),
            )
            .join(ScoreModel, ScoreModel.document_id == DocumentModel.id)
            .group_by(DocumentModel.id)
            .order_by(func.sum(ScoreModel.correct_count).desc())
            .all()
        )
        results = []
        for r in rows:
            total_correct = r.total_correct or 0
            total_possible = r.total_possible or 1
            results.append({
                "doc_id": r.doc_id,
                "doc_title": r.doc_title,
                "total_correct": int(total_correct),
                "total_possible": int(r.total_possible or 0),
                "attempt_count": int(r.attempt_count or 0),
                "accuracy": round(total_correct / total_possible, 4) if total_possible else 0.0,
                "last_attempt": r.last_attempt.isoformat() if r.last_attempt else None,
            })
        return results

    def get_recent_scores(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Latest scores with document title for the badge feed."""
        from app.database.models import DocumentModel
        rows = (
            self._db.query(
                ScoreModel.id,
                ScoreModel.document_id,
                DocumentModel.title.label("doc_title"),
                ScoreModel.correct_count,
                ScoreModel.total_count,
                ScoreModel.timestamp,
            )
            .join(DocumentModel, DocumentModel.id == ScoreModel.document_id)
            .order_by(ScoreModel.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "doc_id": r.document_id,
                "doc_title": r.doc_title,
                "correct_count": r.correct_count,
                "total_count": r.total_count,
                "timestamp": r.timestamp.isoformat() if r.timestamp else None,
            }
            for r in rows
        ]
