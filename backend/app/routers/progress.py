"""Progress-tracking routes with DB-backed persistence."""

from __future__ import annotations

import logging
from typing import Optional

from app.dto import DocumentStatusResponse
from app.dto.documents import DocumentState
from app.services.state_machine import ProgressTracker
from fastapi import APIRouter, HTTPException, Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/progress")

# In-memory tracker cache (kept for real-time fast-path; DB is source of truth)
_trackers: dict[int, ProgressTracker] = {}

# ── Human-readable stage text ─────────────────────────────────────
_STAGE_LABELS: dict[DocumentState, str] = {
    DocumentState.UPLOADED: "Uploaded – waiting to start",
    DocumentState.READING: "Reading PDF",
    DocumentState.PARSING: "Parsing text",
    DocumentState.ANALYZING: "Identifying themes",
    DocumentState.GRAPH_BUILDING: "Building graph",
    DocumentState.QUIZ_GENERATING: "Generating quizzes",
    DocumentState.COMPLETED: "Complete!",
    DocumentState.FAILED: "Failed",
}


def _get_tracker(doc_id: int) -> ProgressTracker:
    """Fetch or create a ProgressTracker for a given document."""
    if doc_id not in _trackers:
        _trackers[doc_id] = ProgressTracker()
    return _trackers[doc_id]


def default_progress_tracker(
    doc_id: int, to_state: DocumentState, stage_progress: float = 0.0
) -> ProgressTracker:
    """Set (or create) a default tracker for a document — used on upload / pipeline events."""
    tracker = _get_tracker(doc_id)
    if tracker.current_state != to_state:
        tracker.advance(to_state, stage_progress=stage_progress)
    else:
        tracker.stage_progress = max(0.0, min(1.0, stage_progress))
    return tracker


def get_document_status(doc_id: int) -> dict:
    """Return a dict suitable for the /documents/{id}/status endpoint."""
    tracker = _get_tracker(doc_id)
    state = tracker.current_state
    return {
        "document_id": doc_id,
        "stage": state.value,
        "stage_label": _STAGE_LABELS.get(state, state.value),
        "progress": round(tracker.overall_progress * 100, 1),
        "message": tracker.error_msg or _STAGE_LABELS.get(state, ""),
        "error": tracker.error_msg,
    }


# ── Route handlers (can also be accessed via /api/v1/progress) ───


@router.get("/", summary="List progress entries")
async def list_progress() -> list[dict[str, int | str]]:
    """Placeholder — will return real document statuses once the DB layer is wired."""
    return []


@router.get("/{doc_id}", summary="Get document processing status")
async def get_progress(
    doc_id: int = Path(..., ge=1, description="Document ID"),
) -> DocumentStatusResponse:
    """Return current state-machine status for a document."""
    tracker = _get_tracker(doc_id)
    return DocumentStatusResponse(
        document_id=doc_id,
        state=tracker.current_state,
        stage_progress=tracker.stage_progress,
        overall_progress=tracker.overall_progress,
        error_msg=tracker.error_msg,
    )


@router.post("/{doc_id}/advance", summary="Advance document state")
async def advance_state(
    doc_id: int = Path(..., ge=1),
    target_state: str = "next",
    stage_progress: float = 0.0,
) -> DocumentStatusResponse:
    """Manually advance (or simulate) document state. Used by pipeline services."""
    from app.dto.documents import DocumentState

    tracker = _get_tracker(doc_id)

    if target_state == "next":
        tracker.auto_advance(stage_progress=stage_progress)
    elif target_state == "fail":
        tracker.fail("Manual failure trigger", stage_progress=stage_progress)
    elif target_state == "retry":
        tracker.retry()
    else:
        st = DocumentState(target_state)
        tracker.advance(st, stage_progress=stage_progress)

    return DocumentStatusResponse(
        document_id=doc_id,
        state=tracker.current_state,
        stage_progress=tracker.stage_progress,
        overall_progress=tracker.overall_progress,
        error_msg=tracker.error_msg,
    )
