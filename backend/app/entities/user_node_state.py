"""Domain entity — UserNodeState."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserNodeState:
    """A mastery-tracking record for a knowledge-graph node.

    States:
      new      – never studied
      reviewing – studied, not yet mastered
      learned   – mastered (avg score >= 80% over 2+ attempts)
    """

    id: Optional[int] = None
    node_id: int = 0
    state: str = "new"          # "new" | "reviewing" | "learned"
    last_reviewed: Optional[datetime] = None
    review_count: int = 0
    created_at: Optional[datetime] = None
