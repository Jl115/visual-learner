"""Graph DTOs — response shapes for knowledge-graph data."""
from typing import Optional, List
from pydantic import BaseModel, Field

from app.dto.nodes import NodeResponse
from app.dto.edges import EdgeResponse


class GraphNodeResponse(BaseModel):
    """A node in the vis-network graph."""
    id: int
    label: str = Field(..., min_length=1)
    title: Optional[str] = None          # hover tooltip
    value: Optional[float] = 5.0          # controls dot size in vis-network
    color: str = "#4ECDC4"
    group: Optional[str] = None            # theme_category for grouping
    font: Optional[dict] = None           # vis-network font options


class GraphEdgeResponse(BaseModel):
    """An edge in the vis-network graph."""
    id: int
    source: int = Field(..., alias="from")
    target: int = Field(..., alias="to")
    width: Optional[float] = 1.0
    color: Optional[str] = None
    arrows: Optional[str] = "to"          # directed edge

    model_config = {"populate_by_name": True}


class GraphResponse(BaseModel):
    """Full graph payload for a document — nodes + edges ready for vis-network DataSet."""
    document_id: int
    nodes: List[GraphNodeResponse] = Field(default_factory=list)
    edges: List[GraphEdgeResponse] = Field(default_factory=list)
    node_count: int = 0
    edge_count: int = 0
