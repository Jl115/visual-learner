"""Mastery / UserNodeState DTOs."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserNodeStateResponse(BaseModel):
    """Single state record for a node."""

    id: int
    node_id: int
    state: str          # "new" | "reviewing" | "learned"
    last_reviewed: Optional[str] = None
    review_count: int
    created_at: Optional[str] = None

    model_config = {"from_attributes": True}

    @classmethod
    def from_entity(cls, state) -> "UserNodeStateResponse":
        from app.entities.user_node_state import UserNodeState

        return cls(
            id=state.id,
            node_id=state.node_id,
            state=state.state,
            last_reviewed=state.last_reviewed.isoformat() if state.last_reviewed else None,
            review_count=state.review_count,
            created_at=state.created_at.isoformat() if state.created_at else None,
        )


class NodeWithStateResponse(BaseModel):
    """A node enriched with its mastery state (for graph rendering)."""

    id: int
    label: str
    color: str = "#4ECDC4"
    state: str = "new"
    review_count: int = 0
    last_reviewed: Optional[str] = None


class GraphWithStatesResponse(BaseModel):
    """Graph payload enriched with per-node mastery states."""

    document_id: int
    nodes: List[NodeWithStateResponse]
    edges: List[dict]


class UpdateStateRequest(BaseModel):
    """POST body to transition a node's mastery state."""

    node_id: int = Field(..., gt=0)
    state: str = Field(..., pattern=r"^(new|reviewing|learned)$")


class MasteryStatsResponse(BaseModel):
    """Aggregated counts for a document."""

    document_id: int
    total_nodes: int
    new_count: int
    reviewing_count: int
    learned_count: int
    mastery_percent: float = 0.0
