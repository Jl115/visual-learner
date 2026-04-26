from app.config import Settings, get_settings
from app.services.ollama_client import OllamaClient
from app.services.nlp_pipeline import NLPPipeline
from app.services.graph_service import GraphBuilder, GraphService
from app.services.quiz_service import QuizEngine


class DIContainer:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self.ollama = OllamaClient(
            base_url=self.settings.OLLAMA_ENDPOINT,
            api_key=self.settings.OLLAMA_API_KEY,
            model=self.settings.OLLAMA_MODEL,
        )
        self.nlp = NLPPipeline()
        self.graph_builder = GraphBuilder()
        self.graph_service = GraphService(self.graph_builder)
        self.quiz_engine = QuizEngine(self.ollama)
    @property
    def db_url(self) -> str:
        return self.settings.DATABASE_URL


container = DIContainer()
