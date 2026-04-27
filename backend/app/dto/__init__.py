"""Init file for dto module."""

from app.dto.documents import CreateDocumentRequest, DocumentResponse, DocumentState
from app.dto.edges import EdgeResponse
from app.dto.graphs import GraphEdgeResponse, GraphNodeResponse, GraphResponse
from app.dto.nodes import CreateNodeRequest, NodeResponse
from app.dto.progress import DocumentStatusResponse, ProgressResponse
from app.dto.quizzes import Question, QuizAnswerRequest, QuizResponse, QuizResult
from app.dto.scores import (
    AllDocumentStatsResponse,
    DocumentStatsResponse,
    RecentScoresResponse,
    ScoreCreateRequest,
    ScoreListResponse,
    ScoreResponse,
)

__all__ = [
    "CreateDocumentRequest",
    "DocumentResponse",
    "DocumentState",
    "CreateNodeRequest",
    "NodeResponse",
    "EdgeResponse",
    "GraphResponse",
    "GraphNodeResponse",
    "GraphEdgeResponse",
    "QuizResponse",
    "Question",
    "QuizAnswerRequest",
    "QuizResult",
    "ProgressResponse",
    "DocumentStatusResponse",
    "ScoreCreateRequest",
    "ScoreResponse",
    "ScoreListResponse",
    "DocumentStatsResponse",
    "AllDocumentStatsResponse",
    "RecentScoresResponse",
]
