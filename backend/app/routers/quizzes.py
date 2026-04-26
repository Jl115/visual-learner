"""Quiz session routes."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/quizzes")


@router.get("/", summary="List quizzes")
async def list_quizzes() -> list[dict[str, str]]:
    return []
