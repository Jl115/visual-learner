"""Document management routes (Phase 2) using DI container."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

if TYPE_CHECKING:
    from app.repositories.document_repo import DocumentRepository

from app.dependencies import get_doc_repo

router = APIRouter(prefix="/documents")


@router.get("/", summary="List documents")
async def list_documents(
    repo: "DocumentRepository" = Depends(get_doc_repo),
) -> list[dict[str, str]]:
    """Return all documents via the injected repository."""
    docs = repo.list_all(limit=50, offset=0)
    return [
        {
            "id": str(d.id) if d.id else "0",
            "title": d.title or "Untitled",
            "status": d.status,
        }
        for d in docs
    ]


@router.get("/{doc_id}", summary="Get document")
async def get_document(
    doc_id: str,
    repo: "DocumentRepository" = Depends(get_doc_repo),
) -> dict[str, str]:
    """Return a single document by ID."""
    try:
        doc = repo.get_by_id(int(doc_id))
    except (ValueError, TypeError):
        return {"error": "Invalid ID format"}

    if doc is None:
        return {"error": "Document not found"}

    return {
        "id": str(doc.id) if doc.id else "0",
        "title": doc.title or "Untitled",
        "status": doc.status,
    }
