"""Knowledge-graph routes (Phase 2)."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/graphs")


@router.get("/", summary="List graphs")
async def list_graphs() -> list[dict[str, str]]:
    return []


@router.get("/{graph_id}", summary="Get graph")
async def get_graph(graph_id: str) -> dict[str, str]:
    return {"id": graph_id, "name": "placeholder"}
