from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.models import Quiz
import ast

router = APIRouter()

@router.get("/{doc_id}")
def get_quizzes(doc_id: str, node_id: str = None, db: Session = Depends(get_db)):
    q = db.query(Quiz).filter(Quiz.document_id == doc_id)
    if node_id:
        q = q.filter(Quiz.node_id == node_id)
    quizzes = q.all()
    result = []
    for quiz in quizzes:
        try:
            options = ast.literal_eval(quiz.options) if quiz.options else []
        except Exception:
            options = []
        result.append({
            "id": quiz.id,
            "node_id": quiz.node_id,
            "question": quiz.question,
            "options": options,
            "correct_index": quiz.correct_index,
        })
    return result
