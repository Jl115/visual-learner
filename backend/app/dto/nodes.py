"""Node DTOs."""
from pydantic import BaseModel, Field


class CreateNodeRequest(BaseModel):
    """Request body for creating a knowledge graph node."""

    document_id: str = Field(..., min_length=1, description="Parent document UUID")
    label: str = Field(..., min_length=1, max_length=200, description="Node display label")
    summary: str = Field(..., max_length=500, description="Short summary of the node")


class NodeResponse(BaseModel):
    """Response shape for a knowledge graph node."""

    id: str
    label: str
    summary: str
    position_x: float | None = None
    position_y: float | None = None
    color: str = "#4ECDC4"
    weight: float = 0.0

    model_config = {"from_attributes": True}
