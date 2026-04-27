"""Document DTOs."""

from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class DocumentState(StrEnum):
    """Document lifecycle states."""

    UPLOADED = "uploaded"
    READING = "reading"
    PARSING = "parsing"
    ANALYZING = "analyzing"
    GRAPH_BUILDING = "graph_building"
    QUIZ_GENERATING = "quiz_generating"
    COMPLETED = "completed"
    FAILED = "failed"


class CreateDocumentRequest(BaseModel):
    """Request body for creating a new document."""

    title: str = Field(..., min_length=1, max_length=500)
    file_path: str = Field(..., min_length=1)

    @field_validator("file_path")
    @classmethod
    def _validate_ext(cls, v: str) -> str:
        allowed = (".pdf", ".txt", ".md", ".docx")
        lower_v = v.lower()
        if not any(lower_v.endswith(ext) for ext in allowed):
            raise ValueError(f"File must be: {allowed}")
        return v


class DocumentResponse(BaseModel):
    """Response shape for a document."""

    id: int
    title: str
    status: str = "pending"
    created_at: datetime
    updated_at: Optional[datetime] = None
    error_msg: Optional[str] = None

    model_config = {"from_attributes": True}
