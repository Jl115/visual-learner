"""Domain entity classes — Document."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Document:
    """A user-uploaded document with NLP pipeline lifecycle."""

    id: Optional[int] = None
    title: str = ""
    source_path: str = ""
    file_path: Optional[str] = None
    raw_text: Optional[str] = None
    status: str = "pending"
    error_msg: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
