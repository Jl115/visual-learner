"""Init file for dto module."""
from app.dto.documents import CreateDocumentRequest, DocumentResponse, DocumentState
from app.dto.nodes import CreateNodeRequest, NodeResponse
from app.dto.edges import EdgeResponse
from app.dto.graphs import GraphResponse, GraphNodeResponse, GraphEdgeResponse
from app.dto.quizzes import QuizResponse, Question, QuizAnswerRequest, QuizResult
from app.dto.progress import ProgressResponse, DocumentStatusResponse
from app.dto.scores import (
    ScoreCreateRequest,
    ScoreResponse,
    ScoreListResponse,
    DocumentStatsResponse,
    AllDocumentStatsResponse,
    RecentScoresResponse,
)

__all__ = [
    "CreateDocumentRequest", "DocumentResponse", "DocumentState",
    "CreateNodeRequest", "NodeResponse",
    "EdgeResponse",
    "GraphResponse", "GraphNodeResponse", "GraphEdgeResponse",
    "QuizResponse", "Question", "QuizAnswerRequest", "QuizResult",
    "ProgressResponse", "DocumentStatusResponse",
    "ScoreCreateRequest", "ScoreResponse", "ScoreListResponse",
    "DocumentStatsResponse", "AllDocumentStatsResponse", "RecentScoresResponse",
]
