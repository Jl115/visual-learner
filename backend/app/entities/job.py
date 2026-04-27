"""Pipeline job entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    """Represents a document-processing job with lifecycle tracking."""

    id: int | None = None
    doc_id: int = 0
    stage: str = "uploaded"
    progress: float = 0.0
    error_msg: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
