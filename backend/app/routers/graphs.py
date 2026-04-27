"""Knowledge-graph routes (Phase 2) using DI container."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends

if TYPE_CHECKING:
    from app.services.graph_service import GraphService

from app.dependencies import get_graph_service

router = APIRouter(prefix="/graphs")


@router.get("/", summary="List graphs")
async def list_graphs(
    service: "GraphService" = Depends(get_graph_service),
) -> list[dict[str, str]]:
    return [{"id": "placeholder", "name": "graph"}]


@router.get("/{graph_id}", summary="Get graph")
async def get_graph(
    graph_id: str,
    service: "GraphService" = Depends(get_graph_service),
) -> dict[str, str]:
    return {"id": graph_id, "name": "placeholder"}
