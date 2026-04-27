"""Score / persistence service."""

from typing import Any, Dict

from app.entities.score import Score
from app.repositories.score_repo import ScoreRepository


class ScoreService:
    """Business-logic wrapper around ScoreRepository.

    Aggregates data for charts and badges while keeping the repository
    free from presentation concerns.
    """

    def __init__(self, repo: ScoreRepository) -> None:
        self._repo = repo

    def record(self, doc_id: int, quiz_id: int, correct: int, total: int) -> Score:
        """Persist a new score record."""
        return self._repo.create(
            Score(
                doc_id=doc_id,
                quiz_id=quiz_id,
                correct_count=correct,
                total_count=total,
            )
        )

    def get_document_stats(self, doc_id: int) -> Dict[str, Any]:
        """Aggregated stats for the bar chart."""
        return self._repo.get_document_stats(doc_id)

    def get_all_document_stats(self) -> list[Dict[str, Any]]:
        """Per-document performance summary (used by dashboard)."""
        return self._repo.get_all_document_stats()

    def get_recent(self, limit: int = 20) -> list[Dict[str, Any]]:
        """Latest feeds for the StatsBadge."""
        return self._repo.get_recent_scores(limit=limit)
