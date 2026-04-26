"""DTO package: request/response schemas."""
from app.dto.documents import CreateDocumentRequest, DocumentResponse, DocumentState
from app.dto.nodes import CreateNodeRequest, NodeResponse
from app.dto.edges import EdgeResponse
from app.dto.quizzes import QuizResponse, Question, QuizAnswerRequest, QuizResult
from app.dto.progress import ProgressResponse

__all__ = [
    "CreateDocumentRequest", "DocumentResponse", "DocumentState",
    "CreateNodeRequest", "NodeResponse",
    "EdgeResponse",
    "QuizResponse", "Question", "QuizAnswerRequest", "QuizResult",
    "ProgressResponse",
]
