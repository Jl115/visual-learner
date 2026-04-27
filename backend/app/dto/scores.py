"""Score DTOs for API request/response shapes."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ScoreCreateRequest(BaseModel):
    """POST /scores body."""

    doc_id: int = Field(..., gt=0, description="Document ID the quiz belongs to")
    quiz_id: int = Field(..., gt=0, description="Quiz ID that was taken")
    correct_count: int = Field(..., ge=0, description="Number of correct answers")
    total_count: int = Field(..., gt=0, description="Total number of questions")


class ScoreResponse(BaseModel):
    """Single score record."""

    id: int
    doc_id: int
    quiz_id: int
    correct_count: int
    total_count: int
    timestamp: Optional[str] = None
    accuracy: float = 0.0

    model_config = {"from_attributes": True}

    @classmethod
    def from_entity(cls, score) -> "ScoreResponse":
        total = score.total_count or 1
        return cls(
            id=score.id,
            doc_id=score.doc_id,
            quiz_id=score.quiz_id,
            correct_count=score.correct_count,
            total_count=score.total_count,
            timestamp=score.timestamp.isoformat() if score.timestamp else None,
            accuracy=round(score.correct_count / total, 4),
        )


class DocumentStatsResponse(BaseModel):
    """Aggregated performance for one document (chart data)."""

    doc_id: int
    doc_title: Optional[str] = None
    total_correct: int
    total_possible: int
    attempt_count: int
    accuracy: float
    last_attempt: Optional[str] = None


class ScoreListResponse(BaseModel):
    """List wrapper."""

    items: List[ScoreResponse]


class AllDocumentStatsResponse(BaseModel):
    """Wrapper for per-document aggregated stats."""

    items: List[DocumentStatsResponse]


class RecentScoresResponse(BaseModel):
    """Recent score feed for the StatsBadge."""

    items: List[dict]
