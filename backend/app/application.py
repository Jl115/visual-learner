"""
Application class — wraps the FastAPI app and DI container.
"""

from __future__ import annotations

from fastapi import APIRouter, FastAPI


class Application:
    def __init__(self, app: FastAPI) -> None:
        self.app = app

    def register_routes(self) -> None:
        api_router = APIRouter(prefix="/api/v1")

        from app.routers import documents, graphs, progress, quizzes, scores

        api_router.include_router(documents, tags=["Documents"])
        api_router.include_router(graphs, tags=["Graphs"])
        api_router.include_router(quizzes, tags=["Quizzes"])
        api_router.include_router(progress, tags=["Progress"])
        api_router.include_router(scores, tags=["Scores"])

        self.app.include_router(api_router)

    def register_middleware(self) -> None:
        pass
