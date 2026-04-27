"""Global exception handler — returns consistent JSON error responses."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


def _error_payload(error: str, detail: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": error, "detail": detail},
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    return _error_payload(
        error=type(exc).__name__,
        detail=str(exc.detail),
        status_code=exc.status_code,
    )


async def catchall_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return _error_payload(
        error="InternalServerError",
        detail="An unexpected error occurred. Please try again later.",
        status_code=500,
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Wire global exception handlers into the FastAPI app."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, catchall_exception_handler)
