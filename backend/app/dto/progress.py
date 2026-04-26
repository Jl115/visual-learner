"""Progress DTOs."""
from pydantic import BaseModel


class ProgressResponse(BaseModel):
    """Response shape for document processing progress."""

    document_id: str
    stage: str
    progress: float  # 0.0 - 1.0
    message: str = ""

    model_config = {"from_attributes": True}
