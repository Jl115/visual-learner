from typing import Optional, List
from app.domains.quiz import Quiz


class QuizRepo:
    def get(self, id: int) -> Optional[Quiz]:
        raise NotImplementedError

    def list_by_document(self, document_id: int) -> List[Quiz]:
        raise NotImplementedError

    def create(self, quiz: Quiz) -> Quiz:
        raise NotImplementedError
