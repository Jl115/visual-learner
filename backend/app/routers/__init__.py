"""API route registrars.

Each submodule exposes a `router: APIRouter` instance.
They are collected here and mounted in `Application.register_routes()`.
"""

from app.routers.documents import router as documents
from app.routers.graphs import router as graphs
from app.routers.mastery import router as mastery
from app.routers.progress import router as progress
from app.routers.quizzes import router as quizzes
from app.routers.scores import router as scores
from app.routers.upload import router as upload

__all__ = ["documents", "graphs", "mastery", "progress", "quizzes", "scores", "upload"]
