"""
FastAPI Application Factory — single entry point for the Visual Learner backend.

Usage:
    uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
    # or
    python -m app.main
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from app.application import Application
from app.config import get_settings
from app.middleware.error_handler import setup_exception_handlers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    settings.configure_logging()
    logger.info("🚀  Lifespan startup  |  version=%s", settings.APP_VERSION)

    # --- STARTUP ---
    yield

    # --- SHUTDOWN ---
    logger.info("👋  Lifespan shutdown complete")


def create_app(**kwargs: Any) -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Visual Learner API",
        description="Backend service for the Visual Learner knowledge-management platform.",
        version=settings.APP_VERSION,
        lifespan=lifespan,
        **kwargs,
    )

    # CORS
    _origins: list[str] = [
        "*",
        "file://*",
        "http://localhost:*",
        "https://localhost:*",
    ]

    env = kwargs.get("env", "dev")
    if env == "production":
        _origins = [
            "file://",
            "http://localhost:*",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.debug("🌐  CORS configured for origins: %s", _origins)

    application = Application(app)
    application.register_routes()
    application.register_middleware()
    setup_exception_handlers(app)

    @app.get("/health", tags=["Health"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": settings.APP_VERSION}

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:create_app",
        factory=True,
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
