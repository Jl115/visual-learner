from app.services.ollama_client import OllamaClient
from app.services.nlp_pipeline import NLPPipeline
from app.services.graph_service import GraphBuilder, GraphService
from app.services.quiz_service import QuizEngine


class DIContainer:
    def __init__(self):
        self.ollama = OllamaClient()
        self.nlp = NLPPipeline()
        self.graph_builder = GraphBuilder()
        self.graph_service = GraphService(self.graph_builder)
        self.quiz_engine = QuizEngine(self.ollama)


container = DIContainer()
