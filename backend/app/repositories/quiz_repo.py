"""Quiz repository — full CRUD."""

import json
from typing import List, Optional
from sqlalchemy.orm import Session

from app.database.models import QuizModel, QuizQuestionModel
from app.entities.quiz import Quiz, Question
from app.repositories.base_repository import BaseRepository


class QuizRepository(BaseRepository):
    """CRUD repository for Quiz entities."""

    _model_cls = QuizModel

    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_domain(self, model: QuizModel) -> Quiz:
        return Quiz(
            id=model.id,
            doc_id=model.doc_id,
            node_id=model.node_id,
            total_questions=model.total_questions,
            questions=[self._question_to_domain(q) for q in model.questions],
            created_at=model.created_at,
        )

    def _question_to_domain(self, model: QuizQuestionModel) -> Question:
        options: List[str] = []
        try:
            options = json.loads(model.options_json)
        except (json.JSONDecodeError, TypeError):
            options = []
        return Question(
            id=model.id,
            quiz_id=model.quiz_id,
            text=model.question,
            options=options,
            correct_index=model.correct_index,
            explanation=model.explanation,
        )

    def _to_model(self, domain: Quiz) -> QuizModel:
        return QuizModel(
            id=domain.id,
            doc_id=domain.doc_id,
            node_id=domain.node_id,
            total_questions=domain.total_questions,
        )

    def get_by_id(self, quiz_id: int) -> Optional[Quiz]:
        model = self._db.query(QuizModel).filter_by(id=quiz_id).first()
        return self._to_domain(model) if model else None

    def list_by_document(self, doc_id: int, limit: int = 50, offset: int = 0) -> List[Quiz]:
        rows = (
            self._db.query(QuizModel)
            .filter_by(doc_id=doc_id)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def list_all(self, limit: int = 50, offset: int = 0) -> List[Quiz]:
        rows = self._db.query(QuizModel).offset(offset).limit(limit).all()
        return [self._to_domain(r) for r in rows]

    def create(self, domain: Quiz) -> Quiz:
        model = self._to_model(domain)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        for q in domain.questions:
            q_model = QuizQuestionModel(
                quiz_id=model.id,
                question=q.text,
                options_json=json.dumps(q.options),
                correct_index=q.correct_index,
                explanation=q.explanation,
            )
            self._db.add(q_model)
        if domain.questions:
            model.total_questions = len(domain.questions)
            self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def delete(self, quiz_id: int) -> bool:
        model = self._db.query(QuizModel).filter_by(id=quiz_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
