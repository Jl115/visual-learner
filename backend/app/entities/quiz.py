"""Domain entity classes — Quiz + Question."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Question:
    """A single multiple-choice question inside a quiz."""

    id: Optional[int] = None
    quiz_id: int = 0
    text: str = ""
    options: List[str] = field(default_factory=list)
    correct_index: int = 0
    explanation: Optional[str] = None


@dataclass
class Quiz:
    """A generated quiz tied to a document (optionally a specific node)."""

    id: Optional[int] = None
    doc_id: int = 0
    node_id: Optional[int] = None
    total_questions: int = 0
    questions: List[Question] = field(default_factory=list)
    created_at: Optional[datetime] = None
