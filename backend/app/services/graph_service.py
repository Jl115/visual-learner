from typing import List
from app.entities.node import Node
from app.entities.edge import Edge


class GraphBuilder:
    def build(self, document_text: str) -> tuple[List[Node], List[Edge]]:
        # Placeholder – real implementation uses NLP + graph algo
        return [], []


class GraphService:
    def __init__(self, builder: GraphBuilder):
        self.builder = builder

    def generate_graph(self, text: str) -> tuple[List[Node], List[Edge]]:
        return self.builder.build(text)
