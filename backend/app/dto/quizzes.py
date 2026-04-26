"""Quiz DTOs."""
from pydantic import BaseModel, Field


class Question(BaseModel):
    """A single quiz question."""

    id: str
    text: str = Field(..., alias="question_text")
    options: list[str] = Field(default_factory=list, alias="options_json")
    correct_index: int = 0
    explanation: str | None = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class QuizResponse(BaseModel):
    """Response shape for a quiz."""

    id: str
    document_id: str
    questions: list[Question] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class QuizAnswerRequest(BaseModel):
    """Request body for submitting an answer."""

    question_id: str = Field(..., min_length=1)
    selected_index: int = Field(..., ge=0)


class QuizResult(BaseModel):
    """Result of a completed quiz."""

    score: int
    total: int
    correct_answers: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}
