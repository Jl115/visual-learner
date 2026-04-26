from typing import Optional, List
from app.domains.node import Node


class NodeRepo:
    def get(self, id: int) -> Optional[Node]:
        raise NotImplementedError

    def list_by_document(self, document_id: int) -> List[Node]:
        raise NotImplementedError

    def create(self, node: Node) -> Node:
        raise NotImplementedError
