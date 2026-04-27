"""Edge repository — full CRUD."""

from typing import List, Optional

from app.database.models import EdgeModel
from app.entities.edge import Edge
from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session


class EdgeRepository(BaseRepository):
    """CRUD repository for Edge entities."""

    _model_cls = EdgeModel

    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_domain(self, model: EdgeModel) -> Edge:
        return Edge(
            id=model.id,
            source_node_id=model.source_node_id,
            target_node_id=model.target_node_id,
            doc_id=model.doc_id,
            relation_type=model.relation_type,
            strength=model.strength,
        )

    def _to_model(self, domain: Edge) -> EdgeModel:
        return EdgeModel(
            id=domain.id,
            source_node_id=domain.source_node_id,
            target_node_id=domain.target_node_id,
            doc_id=domain.doc_id,
            relation_type=domain.relation_type,
            strength=domain.strength,
        )

    def get_by_id(self, edge_id: int) -> Optional[Edge]:
        model = self._db.query(EdgeModel).filter_by(id=edge_id).first()
        return self._to_domain(model) if model else None

    def list_by_document(
        self, doc_id: int, limit: int = 500, offset: int = 0
    ) -> List[Edge]:
        rows = (
            self._db.query(EdgeModel)
            .filter_by(doc_id=doc_id)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def list_by_nodes(self, source_id: int, target_id: int) -> List[Edge]:
        rows = (
            self._db.query(EdgeModel)
            .filter_by(source_node_id=source_id, target_node_id=target_id)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def list_all(self, limit: int = 50, offset: int = 0) -> List[Edge]:
        rows = self._db.query(EdgeModel).offset(offset).limit(limit).all()
        return [self._to_domain(r) for r in rows]

    def create(self, domain: Edge) -> Edge:
        model = self._to_model(domain)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def delete(self, edge_id: int) -> bool:
        model = self._db.query(EdgeModel).filter_by(id=edge_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
