"""Backend application container."""

from __future__ import annotations

# Re-export the production DI container so routers can import from a stable
# top-level location (`app.container`) without tying themselves to the internal
# `app.di` package layout.
from app.di.container import Container, get_container

__all__ = ["Container", "get_container"]
