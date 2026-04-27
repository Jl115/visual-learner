"""Document upload routes — file streaming via multipart/form-data."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Annotated

from app.dependencies import ContainerDep
from app.dto.documents import CreateDocumentRequest, DocumentState
from app.routers.progress import default_progress_tracker
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents")

# Upload storage directory (mirrors the DB location convention)
_UPLOAD_DIR = Path.home() / ".visual-learner" / "uploads"


@router.post(
    "/upload",
    summary="Upload a document via multipart/form-data",
    response_description="Created document metadata",
)
async def upload_document(
    container: ContainerDep,
    file: Annotated[
        UploadFile, File(..., description="Binary document file (PDF, TXT, MD, DOCX)")
    ],
) -> dict[str, str]:
    """Receive raw binary, persist to disk, create a Document record, and return metadata."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Validate extension
    allowed = {".pdf", ".txt", ".md", ".docx"}
    lower_name = file.filename.lower()
    if not any(lower_name.endswith(ext) for ext in allowed):
        raise HTTPException(
            status_code=400, detail=f"Unsupported file type. Allowed: {allowed}"
        )

    # Ensure upload dir exists
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Save file
    file_path = _UPLOAD_DIR / file.filename
    try:
        with file_path.open("wb") as fh:
            shutil.copyfileobj(file.file, fh)
    except OSError as exc:
        logger.error("Failed to save upload: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to save file") from exc
    finally:
        await file.close()

    # Create database record via injected repository
    doc_repo = container.document_repository
    doc = doc_repo.create(
        CreateDocumentRequest(title=file.filename, file_path=str(file_path))
    )

    # Create initial pipeline job for progress tracking
    if doc.id is not None:
        job_repo = container.job_repository
        job_repo.create(doc_id=doc.id)
        default_progress_tracker(doc.id, DocumentState.UPLOADED)

    logger.info("Document uploaded: id=%s title=%s", doc.id, doc.title)

    return {
        "id": str(doc.id or 0),
        "title": doc.title,
        "path": str(file_path),
        "status": doc.status,
    }
