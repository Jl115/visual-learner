"""Score routes — full CRUD + aggregation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.dependencies import get_score_repo
from app.dto.scores import (
    AllDocumentStatsResponse,
    DocumentStatsResponse,
    RecentScoresResponse,
    ScoreCreateRequest,
    ScoreListResponse,
    ScoreResponse,
)
from fastapi import APIRouter, Depends, HTTPException, status

if TYPE_CHECKING:
    from app.repositories.score_repo import ScoreRepository

router = APIRouter(prefix="/scores")


@router.post(
    "/", summary="Record a new quiz score", status_code=status.HTTP_201_CREATED
)
async def create_score(
    req: ScoreCreateRequest,
    repo: "ScoreRepository" = Depends(get_score_repo),
) -> ScoreResponse:
    """Persist the result of a completed quiz."""
    from app.entities.score import Score

    score = repo.create(
        Score(
            doc_id=req.doc_id,
            quiz_id=req.quiz_id,
            correct_count=req.correct_count,
            total_count=req.total_count,
        )
    )
    return ScoreResponse.from_entity(score)


@router.get("/", summary="List all recent scores")
async def list_scores(
    repo: "ScoreRepository" = Depends(get_score_repo),
) -> ScoreListResponse:
    """Return the latest score entries (newest first)."""
    from pydantic import TypeAdapter

    scores = repo.list_all(limit=50)
    items = [ScoreResponse.from_entity(s) for s in scores]
    return ScoreListResponse(items=items)


@router.get("/document/{doc_id}", summary="Scores for a document")
async def get_document_scores(
    doc_id: int,
    repo: "ScoreRepository" = Depends(get_score_repo),
) -> ScoreListResponse:
    """All quiz attempts for a single document."""
    scores = repo.list_by_document(doc_id, limit=50)
    items = [ScoreResponse.from_entity(s) for s in scores]
    return ScoreListResponse(items=items)


@router.get("/stats/{doc_id}", summary="Aggregated stats for a document")
async def get_document_stats(
    doc_id: int,
    repo: "ScoreRepository" = Depends(get_score_repo),
) -> DocumentStatsResponse:
    """Total correct, total possible, accuracy, attempt count."""
    stats = repo.get_document_stats(doc_id)
    return DocumentStatsResponse(**stats)


@router.get("/stats", summary="All document performance stats")
async def get_all_document_stats(
    repo: "ScoreRepository" = Depends(get_score_repo),
) -> AllDocumentStatsResponse:
    """Per-document aggregated data — used for the dashboard bar chart."""
    items = repo.get_all_document_stats()
    return AllDocumentStatsResponse(items=[DocumentStatsResponse(**s) for s in items])


@router.get("/recent", summary="Recent activity feed")
async def get_recent_scores(
    repo: "ScoreRepository" = Depends(get_score_repo),
) -> RecentScoresResponse:
    """Recent score entries with document titles — shows in StatsBadge."""
    return RecentScoresResponse(items=repo.get_recent_scores(limit=20))
