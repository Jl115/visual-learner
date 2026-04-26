from datetime import datetime
from typing import Any, List, Optional
import json

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

from app.domains.document import Document
from app.domains.node import Node
from app.domains.edge import Edge
from app.domains.quiz import Quiz, Question

Base = declarative_base()


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    nodes = relationship("NodeModel", back_populates="document", cascade="all, delete-orphan")
    edges = relationship("EdgeModel", back_populates="document", cascade="all, delete-orphan")
    quizzes = relationship("QuizModel", back_populates="document", cascade="all, delete-orphan")

    def to_domain(self) -> Document:
        return Document(
            id=self.id,
            title=self.title,
            file_path=self.path,
        )


class NodeModel(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    label = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)

    document = relationship("DocumentModel", back_populates="nodes")

    def to_domain(self) -> Node:
        return Node(
            id=self.id,
            label=self.label,
            document_id=self.doc_id,
        )


class EdgeModel(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, index=True)
    source_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    target_node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    doc_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    document = relationship("DocumentModel", back_populates="edges")

    def to_domain(self) -> Edge:
        return Edge(
            id=self.id,
            source_id=self.source_node_id,
            target_id=self.target_node_id,
            relation="",
        )


class QuizModel(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("DocumentModel", back_populates="quizzes")
    questions = relationship("QuizQuestionModel", back_populates="quiz", cascade="all, delete-orphan")

    def to_domain(self) -> Quiz:
        return Quiz(
            id=self.id,
            document_id=self.doc_id,
            questions=[q.to_domain() for q in self.questions],
        )


class QuizQuestionModel(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False, default="[]")
    correct_index = Column(Integer, nullable=False, default=0)

    quiz = relationship("QuizModel", back_populates="questions")

    def to_domain(self) -> Question:
        options: List[str] = []
        try:
            options = json.loads(self.options_json)
        except json.JSONDecodeError:
            options = []
        return Question(
            id=self.id,
            text=self.question,
            options=options,
            correct_index=self.correct_index,
        )
