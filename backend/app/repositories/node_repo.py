"""Node repository — full CRUD."""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.models import NodeModel
from app.entities.node import Node
from app.repositories.base_repository import BaseRepository


class NodeRepository(BaseRepository):
    """CRUD repository for Node entities."""

    _model_cls = NodeModel

    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_domain(self, model: NodeModel) -> Node:
        return Node(
            id=model.id,
            doc_id=model.doc_id,
            label=model.label,
            summary=model.summary,
            position_x=model.position_x,
            position_y=model.position_y,
            weight=model.weight,
            color=model.color,
            theme_category=model.theme_category,
            full_text=model.full_text,
        )

    def _to_model(self, domain: Node) -> NodeModel:
        return NodeModel(
            id=domain.id,
            doc_id=domain.doc_id,
            label=domain.label,
            summary=domain.summary,
            position_x=domain.position_x,
            position_y=domain.position_y,
            weight=domain.weight,
            color=domain.color,
            theme_category=domain.theme_category,
            full_text=domain.full_text,
        )

    def get_by_id(self, node_id: int) -> Optional[Node]:
        model = self._db.query(NodeModel).filter_by(id=node_id).first()
        return self._to_domain(model) if model else None

    def list_by_document(self, doc_id: int, limit: int = 200, offset: int = 0) -> List[Node]:
        rows = (
            self._db.query(NodeModel)
            .filter_by(doc_id=doc_id)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def list_all(self, limit: int = 50, offset: int = 0) -> List[Node]:
        rows = self._db.query(NodeModel).offset(offset).limit(limit).all()
        return [self._to_domain(r) for r in rows]

    def create(self, domain: Node) -> Node:
        model = self._to_model(domain)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def update(self, node_id: int, **kwargs) -> Optional[Node]:
        model = self._db.query(NodeModel).filter_by(id=node_id).first()
        if not model:
            return None
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def delete(self, node_id: int) -> bool:
        model = self._db.query(NodeModel).filter_by(id=node_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
