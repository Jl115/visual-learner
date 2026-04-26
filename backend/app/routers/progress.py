"""Progress-tracking routes."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/progress")


@router.get("/", summary="List progress entries")
async def list_progress() -> list[dict[str, int | str]]:
    return []
