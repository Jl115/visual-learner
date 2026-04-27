from typing import Dict, List, Optional

import networkx as nx
from app.entities.edge import Edge
from app.entities.node import Node
from app.repositories.node_repo import NodeRepository
from app.repositories.edge_repo import EdgeRepository
from app.services.nlp_pipeline import NLPPipeline
from app.services.ollama_client import OllamaClient

from app.dto.graphs import GraphResponse, GraphNodeResponse, GraphEdgeResponse


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
        edge_repo: EdgeRepository | None = None,
    ) -> None:
        self.repo = repo
        self.ollama = ollama
        self.builder = builder or GraphBuilder()
        self.edge_repo = edge_repo

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

    def get_document_graph(self, doc_id: int) -> Optional[GraphResponse]:
        """
        Fetch nodes and edges for a document and assemble a
        vis-network–ready GraphResponse payload.
        """
        nodes = self.repo.list_by_document(doc_id)
        edges: List[Edge] = []
        if self.edge_repo is not None:
            edges = self.edge_repo.list_by_document(doc_id)

        node_responses: List[GraphNodeResponse] = []
        for n in nodes:
            node_responses.append(GraphNodeResponse(
                id=n.id or -1,
                label=n.label,
                title=n.summary,
                value=n.weight if n.weight is not None else 5.0,
                color=n.color,
                group=n.theme_category,
                font={"color": "#f0f0f0", "face": "Inter, system-ui, sans-serif"},
            ))

        edge_responses: List[GraphEdgeResponse] = []
        for e in edges:
            # inherit edge color from source node for visual continuity
            source_color = "#666666"
            src_node = next((n for n in nodes if n.id == e.source_node_id), None)
            if src_node:
                source_color = src_node.color

            edge_responses.append(GraphEdgeResponse(
                id=e.id or -1,
                source=e.source_node_id,
                target=e.target_node_id,
                width=e.strength if e.strength is not None else 1.0,
                color=source_color,
                arrows="to",
            ))

        return GraphResponse(
            document_id=doc_id,
            nodes=node_responses,
            edges=edge_responses,
            node_count=len(node_responses),
            edge_count=len(edge_responses),
        )
