"""Knowledge-graph routes (Phase 2) using DI container."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND

if TYPE_CHECKING:
    from app.services.graph_service import GraphService

from app.dependencies import get_graph_service

from app.dto.graphs import GraphResponse

router = APIRouter(prefix="/graphs")


@router.get("/", summary="List graphs")
async def list_graphs(
    service: "GraphService" = Depends(get_graph_service),
) -> list[dict[str, str]]:
    return [{"id": "placeholder", "name": "graph"}]


@router.get("/{doc_id}", summary="Get graph for a document")
async def get_graph(
    doc_id: int,
    service: "GraphService" = Depends(get_graph_service),
) -> GraphResponse:
    graph = service.get_document_graph(doc_id)
    if graph is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail=f"Graph for document {doc_id} not found")
    return graph
