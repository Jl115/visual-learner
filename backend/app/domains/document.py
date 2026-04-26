from dataclasses import dataclass
from typing import Optional


@dataclass
class Document:
    id: Optional[int] = None
    title: str = ""
    content: str = ""
    file_path: Optional[str] = None
