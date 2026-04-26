"""DTO package: request/response schemas for all endpoints."""
from backend.app.dto.documents import CreateDocumentRequest, DocumentResponse
from backend.app.dto.nodes import CreateNodeRequest, NodeResponse
from backend.app.dto.edges import EdgeResponse
from backend.app.dto.quizzes import QuizResponse, Question, QuizAnswerRequest, QuizResult
from backend.app.dto.progress import ProgressResponse

__all__ = [
    "CreateDocumentRequest",
    "DocumentResponse",
    "CreateNodeRequest",
    "NodeResponse",
    "EdgeResponse",
    "QuizResponse",
    "Question",
    "QuizAnswerRequest",
    "QuizResult",
    "ProgressResponse",
]
