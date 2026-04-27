"""Progress-tracking routes."""

from __future__ import annotations

from app.dto.progress import DocumentStatusResponse
from app.services.state_machine import ProgressTracker
from fastapi import APIRouter, Path

router = APIRouter(prefix="/progress")

# In-memory tracker cache (replace with Redis or DB later)
_trackers: dict[int, ProgressTracker] = {}


def _get_tracker(doc_id: int) -> ProgressTracker:
    """Fetch or create a ProgressTracker for a given document."""
    if doc_id not in _trackers:
        _trackers[doc_id] = ProgressTracker()
    return _trackers[doc_id]


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
