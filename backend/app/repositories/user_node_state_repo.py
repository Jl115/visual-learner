"""UserNodeState repository — CRUD + aggregation for mastery tracking."""

from typing import Dict, List, Optional

from app.database.models import UserNodeStateModel
from app.entities.user_node_state import UserNodeState
from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session


class UserNodeStateRepository(BaseRepository):
    """CRUD + aggregation for user_node_states."""

    _model_cls = UserNodeStateModel

    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_domain(self, model: UserNodeStateModel) -> UserNodeState:
        return UserNodeState(
            id=model.id,
            node_id=model.node_id,
            state=model.state,
            last_reviewed=model.last_reviewed,
            review_count=model.review_count,
            created_at=model.created_at,
        )

    def _to_model(self, domain: UserNodeState) -> UserNodeStateModel:
        return UserNodeStateModel(
            id=domain.id,
            node_id=domain.node_id,
            state=domain.state,
            last_reviewed=domain.last_reviewed,
            review_count=domain.review_count,
            created_at=domain.created_at,
        )

    def get_by_id(self, state_id: int) -> Optional[UserNodeState]:
        model = self._db.query(UserNodeStateModel).filter_by(id=state_id).first()
        return self._to_domain(model) if model else None

    def get_by_node_id(self, node_id: int) -> Optional[UserNodeState]:
        """Fetch state for a specific node (one record per node)."""
        model = self._db.query(UserNodeStateModel).filter_by(node_id=node_id).first()
        return self._to_domain(model) if model else None

    def list_all(self, limit: int = 200, offset: int = 0) -> List[UserNodeState]:
        rows = (
            self._db.query(UserNodeStateModel)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def list_by_document(self, doc_id: int, limit: int = 200, offset: int = 0) -> List[UserNodeState]:
        """Return states for all nodes of a document via JOIN."""
        from app.database.models import NodeModel

        rows = (
            self._db.query(UserNodeStateModel)
            .join(NodeModel, UserNodeStateModel.node_id == NodeModel.id)
            .filter(NodeModel.doc_id == doc_id)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def create(self, domain: UserNodeState) -> UserNodeState:
        model = self._to_model(domain)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def update_or_create(
        self, node_id: int, **kwargs
    ) -> UserNodeState:
        """Upsert: update an existing record or create a new one for the node."""
        model = self._db.query(UserNodeStateModel).filter_by(node_id=node_id).first()
        if model:
            for key, value in kwargs.items():
                if hasattr(model, key):
                    setattr(model, key, value)
            self._db.commit()
            self._db.refresh(model)
            return self._to_domain(model)
        # Create new
        new_domain = UserNodeState(
            node_id=node_id,
            state=kwargs.get("state", "new"),
            review_count=kwargs.get("review_count", 0),
            last_reviewed=kwargs.get("last_reviewed"),
        )
        return self.create(new_domain)

    def delete(self, state_id: int) -> bool:
        model = self._db.query(UserNodeStateModel).filter_by(id=state_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True

    # ------------------------------------------------------------------
    # Aggregation helpers
    # ------------------------------------------------------------------

    def get_document_stats(self, doc_id: int) -> Dict[str, int]:
        """Return counts per state for a document's nodes."""
        from sqlalchemy import func
        from app.database.models import NodeModel

        counts = {
            "new": 0,
            "reviewing": 0,
            "learned": 0,
        }
        rows = (
            self._db.query(UserNodeStateModel.state, func.count(UserNodeStateModel.id))
            .join(NodeModel, UserNodeStateModel.node_id == NodeModel.id)
            .filter(NodeModel.doc_id == doc_id)
            .group_by(UserNodeStateModel.state)
            .all()
        )
        for state, cnt in rows:
            counts[state] = cnt
        return counts

    def get_avg_score_for_node(self, node_id: int) -> float:
        """Look up avg score for quiz attempts on this node's quiz."""
        from sqlalchemy import func
        from app.database.models import QuizAttemptModel, QuizModel

        avg = (
            self._db.query(func.avg(QuizAttemptModel.score))
            .join(QuizModel, QuizAttemptModel.quiz_id == QuizModel.id)
            .filter(QuizModel.node_id == node_id)
            .scalar()
        )
        return float(avg) if avg is not None else 0.0
