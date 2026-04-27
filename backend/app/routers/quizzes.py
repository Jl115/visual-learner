"""Quiz session routes using DI container."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

if TYPE_CHECKING:
    from app.services.quiz_service import QuizEngine

from app.dependencies import get_quiz_service

router = APIRouter(prefix="/quizzes")


@router.get("/", summary="List quizzes")
async def list_quizzes(
    quiz_svc: "QuizEngine" = Depends(get_quiz_service),
) -> list[dict[str, str]]:
    return []
