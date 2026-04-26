"""Edge DTOs."""
from typing import Optional
from pydantic import BaseModel, Field


class EdgeResponse(BaseModel):
    """Response shape for a graph edge."""
    id: int
    source: int = Field(..., alias="source_node_id")
    target: int = Field(..., alias="target_node_id")
    relation: Optional[str] = Field(None, alias="relation_type")

    model_config = {"from_attributes": True, "populate_by_name": True}
