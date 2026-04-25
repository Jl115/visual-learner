"""Score / achievement routes."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/scores")


@router.get("/", summary="List scores")
async def list_scores() -> list[dict[str, int | str]]:
    return []
