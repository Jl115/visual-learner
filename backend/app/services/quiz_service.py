from typing import List

from app.entities.quiz import Question, Quiz
from app.services.ollama_client import OllamaClient


class QuizEngine:
    def __init__(self, ollama: OllamaClient):
        self.ollama = ollama

    async def generate_quiz(self, document_text: str) -> Quiz:
        # Placeholder – real implementation calls Ollama for question generation
        return Quiz(
            questions=[
                Question(
                    text="Sample question?", options=["A", "B", "C"], correct_index=0
                )
            ]
        )
