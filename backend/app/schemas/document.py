from pydantic import BaseModel
from datetime import datetime

class DocumentOut(BaseModel):
    id: str
    filename: str
    raw_text: str
    created_at: datetime

    class Config:
        from_attributes = True
