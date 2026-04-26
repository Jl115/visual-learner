"""Domain entity — Quiz Score."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Score:
    """A persisted quiz score for a document."""

    id: Optional[int] = None
    doc_id: int = 0
    quiz_id: int = 0
    correct_count: int = 0
    total_count: int = 0
    timestamp: Optional[datetime] = None
