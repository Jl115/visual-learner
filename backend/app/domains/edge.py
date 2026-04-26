from dataclasses import dataclass
from typing import Optional


@dataclass
class Edge:
    id: Optional[int] = None
    source_id: int = 0
    target_id: int = 0
    relation: str = ""
