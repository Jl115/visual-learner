"""Mastery service — orchestrates state transitions and scoring."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.entities.user_node_state import UserNodeState
from app.repositories.user_node_state_repo import UserNodeStateRepository
from sqlalchemy.orm import Session


class MasteryService:
    """Business logic for node mastery tracking.

    Rules:
      • New → Reviewing : any quiz attempt
      • Reviewing → Learned : avg score ≥ 80% over 2+ attempts
      • explicit override via update_state()
    """

    _LEARNED_THRESHOLD = 0.80   # 80%
    _MIN_ATTEMPTS = 2

    def __init__(self, db: Session, state_repo: UserNodeStateRepository) -> None:
        self._db = db
        self._repo = state_repo

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_state(self, node_id: int) -> Optional[UserNodeState]:
        """Fetch current mastery state for a node."""
        return self._repo.get_by_node_id(node_id)

    def get_document_states(self, doc_id: int) -> List[UserNodeState]:
        """All node states for a document."""
        return self._repo.list_by_document(doc_id)

    def get_stats(self, doc_id: int) -> Dict[str, int]:
        """Aggregated counts per state."""
        return self._repo.get_document_stats(doc_id)

    def init_node(self, node_id: int) -> UserNodeState:
        """Create a default 'new' state record for a freshly created node."""
        existing = self._repo.get_by_node_id(node_id)
        if existing:
            return existing
        return self._repo.create(
            UserNodeState(node_id=node_id, state="new", review_count=0)
        )

    def record_attempt(self, node_id: int, *, score: float, total: float) -> UserNodeState:
        """Called after a quiz attempt. Updates review_count and possibly transitions state."""
        state = self._repo.update_or_create(
            node_id=node_id,
            state="reviewing",          # at minimum reviewing after any attempt
            review_count=self._repo.get_by_node_id(node_id).review_count + 1
            if self._repo.get_by_node_id(node_id)
            else 1,
            last_reviewed=datetime.now(timezone.utc),
        )

        # Auto-promote to learned?
        if self._should_promote(node_id):
            state = self._repo.update_or_create(
                node_id=node_id,
                state="learned",
                last_reviewed=datetime.now(timezone.utc),
            )
        return state

    def update_state(self, node_id: int, new_state: str) -> UserNodeState:
        """Explicit state transition (manual override / UI action)."""
        if new_state not in {"new", "reviewing", "learned"}:
            raise ValueError(f"Invalid state: {new_state}")
        return self._repo.update_or_create(
            node_id=node_id,
            state=new_state,
            last_reviewed=datetime.now(timezone.utc),
        )

    def reset_node(self, node_id: int) -> UserNodeState:
        """Reset a node back to 'new'."""
        return self._repo.update_or_create(
            node_id=node_id,
            state="new",
            review_count=0,
            last_reviewed=None,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _should_promote(self, node_id: int) -> bool:
        """Return True if avg score >= 80% over >= 2 attempts."""
        avg = self._repo.get_avg_score_for_node(node_id)
        # Need at least MIN_ATTEMPTS attempts — but our repo returns only scores,
        # not attempt count.  We'll fetch attempt count via a separate helper.
        from app.database.models import QuizAttemptModel, QuizModel
        from sqlalchemy import func

        attempt_count = (
            self._db.query(func.count(QuizAttemptModel.id))
            .join(QuizModel, QuizAttemptModel.quiz_id == QuizModel.id)
            .filter(QuizModel.node_id == node_id)
            .scalar()
            or 0
        )
        return attempt_count >= self._MIN_ATTEMPTS and avg >= self._LEARNED_THRESHOLD
