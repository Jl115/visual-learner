from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Question:
    id: Optional[int] = None
    text: str = ""
    options: List[str] = field(default_factory=list)
    correct_index: int = 0


@dataclass
class Quiz:
    id: Optional[int] = None
    document_id: Optional[int] = None
    questions: List[Question] = field(default_factory=list)
