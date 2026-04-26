from typing import Dict, List
import networkx as nx
from app.entities.node import Node
from app.entities.edge import Edge
from app.repositories.node_repo import NodeRepository
from app.services.ollama_client import OllamaClient
from app.services.nlp_pipeline import NLPPipeline


class GraphBuilder:
    """Convenience wrapper around networkx — used as a shared builder dependency."""

    def build(self, document_text: str) -> tuple[List[Node], List[Edge]]:
        # Placeholder – real implementation uses NLP + graph algo
        return [], []


class GraphService:
    """Orchestrates graph construction with injected dependencies."""

    def __init__(
        self,
        repo: NodeRepository,
        ollama: OllamaClient,
        builder: GraphBuilder | None = None,
    ) -> None:
        self.repo = repo
        self.ollama = ollama
        self.builder = builder or GraphBuilder()

    def generate_graph(self, text: str) -> tuple[List[Node], List[Edge]]:
        return self.builder.build(text)

    def build_graph(self, doc_id: str, themes: List[Dict]) -> nx.Graph:
        """Build a networkx graph from themes extracted from a document."""
        graph = nx.Graph()

        for i, theme in enumerate(themes):
            label = theme.get("label", f"Theme {i}")
            summary = theme.get("summary", "")
            weight = theme.get("weight", 1.0)

            graph.add_node(
                label,
                doc_id=doc_id,
                summary=summary,
                weight=weight,
            )

        # Simple edge logic — connect related themes if similarity is provided
        for i, src in enumerate(themes):
            for j, dst in enumerate(themes):
                if i < j:
                    similarity = src.get("similarities", {}).get(dst.get("label"), 0)
                    if similarity > 0.5:
                        graph.add_edge(
                            src["label"],
                            dst["label"],
                            weight=similarity,
                        )

        return graph

    def save_nodes(self, doc_id: str, nodes: List[Node]) -> List[Node]:
        """Persist nodes for a document via the injected repository."""
        return [self.repo.create(node) for node in nodes]
