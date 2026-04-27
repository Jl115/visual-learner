"""Progress DTOs."""

from datetime import datetime
from typing import Optional

from app.dto.documents import DocumentState
from pydantic import BaseModel, Field


class ProgressResponse(BaseModel):
    """Response shape for document processing progress."""

    document_id: int
    stage: str
    progress: float
    message: str = ""

    model_config = {"from_attributes": True}


class DocumentStatusResponse(BaseModel):
    """Full document status with state-machine info."""

    document_id: int
    state: DocumentState
    stage_progress: float = Field(0.0, ge=0.0, le=1.0)
    overall_progress: float = Field(0.0, ge=0.0, le=1.0)
    error_msg: Optional[str] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
