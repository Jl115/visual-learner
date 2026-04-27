"""Mastery-state routes — CRUD + aggregation for node mastery."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.dependencies import get_db, get_mastery_service
from app.dto.mastery import (
    GraphWithStatesResponse,
    MasteryStatsResponse,
    NodeWithStateResponse,
    UpdateStateRequest,
    UserNodeStateResponse,
)
from app.repositories.node_repo import NodeRepository
from app.repositories.user_node_state_repo import UserNodeStateRepository
from app.services.mastery_service import MasteryService
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    pass

router = APIRouter(prefix="/mastery")


# ------------------------------------------------------------------
# Utility: build enriched graph payload
# ------------------------------------------------------------------

def _build_graph_with_states(
    doc_id: int, db: Session
) -> GraphWithStatesResponse:
    node_repo = NodeRepository(db)
    from app.repositories.edge_repo import EdgeRepository

    edge_repo = EdgeRepository(db)
    state_repo = UserNodeStateRepository(db)

    nodes = node_repo.list_by_document(doc_id)
    edges = edge_repo.list_by_document(doc_id)

    enriched_nodes: list[NodeWithStateResponse] = []
    for n in nodes:
        state = state_repo.get_by_node_id(n.id)
        enriched_nodes.append(
            NodeWithStateResponse(
                id=n.id,
                label=n.label,
                color=n.color if state is None else _state_color(state.state),
                state=state.state if state else "new",
                review_count=state.review_count if state else 0,
                last_reviewed=state.last_reviewed.isoformat() if state and state.last_reviewed else None,
            )
        )

    edge_dicts = [
        {
            "id": e.id,
            "from": e.source_id,
            "to": e.target_id,
            "color": e.relation,
        }
        for e in edges
    ]

    return GraphWithStatesResponse(
        document_id=doc_id,
        nodes=enriched_nodes,
        edges=edge_dicts,
    )


def _state_color(state: str) -> str:
    """Map mastery state to DESIGN.md token color."""
    return {
        "new": "#DDA0DD",      # lavender — untouched
        "reviewing": "#FFDAB9",  # peach — in progress
        "learned": "#9CAF88",    # sage — mastered
    }.get(state, "#4ECDC4")


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

@router.get("/graph/{doc_id}", summary="Get graph enriched with mastery states")
async def get_graph_with_states(
    doc_id: int,
    db: Session = Depends(get_db),
) -> GraphWithStatesResponse:
    """Return full graph including per-node mastery state and colors."""
    return _build_graph_with_states(doc_id, db)


@router.get("/stats/{doc_id}", summary="Mastery stats for a document")
async def get_mastery_stats(
    doc_id: int,
    service: MasteryService = Depends(get_mastery_service),
) -> MasteryStatsResponse:
    """Aggregated counts: new, reviewing, learned."""
    stats = service.get_stats(doc_id)
    total = sum(stats.values())
    return MasteryStatsResponse(
        document_id=doc_id,
        total_nodes=total,
        new_count=stats.get("new", 0),
        reviewing_count=stats.get("reviewing", 0),
        learned_count=stats.get("learned", 0),
        mastery_percent=round((stats.get("learned", 0) / total * 100), 2)
        if total else 0.0,
    )


@router.get("/node/{node_id}", summary="Get mastery state for a node")
async def get_node_state(
    node_id: int,
    db: Session = Depends(get_db),
) -> UserNodeStateResponse:
    """Return mastery state record for a single node."""
    repo = UserNodeStateRepository(db)
    state = repo.get_by_node_id(node_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No state record found for node {node_id}",
        )
    return UserNodeStateResponse.from_entity(state)


@router.post("/node", summary="Update mastery state for a node", status_code=status.HTTP_200_OK)
async def update_node_state(
    req: UpdateStateRequest,
    service: MasteryService = Depends(get_mastery_service),
) -> UserNodeStateResponse:
    """Manually transition a node's mastery state (UI override)."""
    state = service.update_state(req.node_id, req.state)
    return UserNodeStateResponse.from_entity(state)


@router.post("/node/{node_id}/attempt", summary="Record a quiz attempt")
async def record_attempt(
    node_id: int,
    score: float = 0.0,
    total: float = 1.0,
    service: MasteryService = Depends(get_mastery_service),
) -> UserNodeStateResponse:
    """Record a quiz score for a node; auto-promotes to learned if threshold met."""
    state = service.record_attempt(node_id, score=score, total=total)
    return UserNodeStateResponse.from_entity(state)


@router.post("/node/{node_id}/reset", summary="Reset a node to 'new'")
async def reset_node(
    node_id: int,
    service: MasteryService = Depends(get_mastery_service),
) -> UserNodeStateResponse:
    """Reset a node's mastery state back to 'new'."""
    state = service.reset_node(node_id)
    return UserNodeStateResponse.from_entity(state)
