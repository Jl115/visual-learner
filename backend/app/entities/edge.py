"""Domain entity classes — Edge."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Edge:
    """A directed relationship between two nodes in the knowledge graph."""

    id: Optional[int] = None
    source_node_id: int = 0
    target_node_id: int = 0
    doc_id: int = 0
    relation_type: Optional[str] = None
    strength: Optional[float] = None
