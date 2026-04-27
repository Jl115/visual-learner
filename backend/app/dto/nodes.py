"""Node DTOs."""

from typing import Optional

from pydantic import BaseModel, Field


class CreateNodeRequest(BaseModel):
    """Request body for creating a knowledge graph node."""

    document_id: int = Field(..., gt=0)
    label: str = Field(..., min_length=1, max_length=200)
    summary: str = Field(..., max_length=500)


class NodeResponse(BaseModel):
    """Response shape for a knowledge graph node."""

    id: int
    label: str
    summary: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    color: str = "#4ECDC4"
    weight: Optional[float] = None

    model_config = {"from_attributes": True}
