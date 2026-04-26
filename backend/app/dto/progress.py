"""Progress DTOs."""
from pydantic import BaseModel


class ProgressResponse(BaseModel):
    """Response shape for document processing progress."""
    document_id: int
    stage: str
    progress: float
    message: str = ""

    model_config = {"from_attributes": True}
