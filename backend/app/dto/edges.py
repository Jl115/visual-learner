"""Edge DTOs."""
from pydantic import BaseModel, Field


class EdgeResponse(BaseModel):
    """Response shape for a graph edge."""

    id: str
    source: str = Field(..., alias="source_node_id", description="Source node UUID")
    target: str = Field(..., alias="target_node_id", description="Target node UUID")
    relation: str | None = Field(None, alias="relation_type", description="Relationship label")

    model_config = {"from_attributes": True, "populate_by_name": True}
