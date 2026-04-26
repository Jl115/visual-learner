from dataclasses import dataclass
from typing import Optional


@dataclass
class Node:
    id: Optional[int] = None
    label: str = ""
    document_id: Optional[int] = None
