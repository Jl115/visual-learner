from typing import Optional, List
from app.domains.edge import Edge


class EdgeRepo:
    def get(self, id: int) -> Optional[Edge]:
        raise NotImplementedError

    def list_by_document(self, document_id: int) -> List[Edge]:
        raise NotImplementedError

    def create(self, edge: Edge) -> Edge:
        raise NotImplementedError
