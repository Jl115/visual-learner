"""Quiz DTOs."""

from typing import List, Optional

from pydantic import BaseModel, Field


class Question(BaseModel):
    """A single quiz question."""

    id: int
    text: str = Field(..., alias="question_text")
    options: List[str] = Field(default_factory=list, alias="options_json")
    correct_index: int = 0
    explanation: Optional[str] = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class QuizResponse(BaseModel):
    """Response shape for a quiz."""

    id: int
    document_id: int
    questions: List[Question] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class QuizAnswerRequest(BaseModel):
    """Request body for submitting an answer."""

    question_id: int = Field(..., gt=0)
    selected_index: int = Field(..., ge=0)


class QuizResult(BaseModel):
    """Result of a completed quiz."""

    score: int
    total: int
    correct_answers: List[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}
