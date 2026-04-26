"""Domain entity classes — Node."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Node:
    """A knowledge-graph node extracted from a document."""

    id: Optional[int] = None
    doc_id: int = 0
    label: str = ""
    summary: Optional[str] = None
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    weight: Optional[float] = None
    color: str = "#4ECDC4"
    theme_category: Optional[str] = None
    full_text: Optional[str] = None
