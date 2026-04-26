"""Document management routes (Phase 2)."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/documents")


@router.get("/", summary="List documents")
async def list_documents() -> list[dict[str, str]]:
    """Placeholder — returns empty list."""
    return []


@router.get("/{doc_id}", summary="Get document")
async def get_document(doc_id: str) -> dict[str, str]:
    """Placeholder."""
    return {"id": doc_id, "title": "placeholder"}
