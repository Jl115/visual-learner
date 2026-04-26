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
    # --- NEW fields for #76 schema ---
    source_path = Column(String, nullable=False, default="")
    raw_text = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="pending")
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    nodes = relationship("NodeModel", back_populates="document", cascade="all, delete-orphan")
    edges = relationship("EdgeModel", back_populates="document", cascade="all, delete-orphan")
    quizzes = relationship("QuizModel", back_populates="document", cascade="all, delete-orphan")
    # --- NEW relationship ---
    scores = relationship("ScoreModel", back_populates="document", cascade="all, delete-orphan")

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
    # --- NEW fields for #76 schema ---
    color = Column(String, nullable=False, default="#4ECDC4")
    theme_category = Column(String, nullable=True)
    full_text = Column(Text, nullable=True)

    document = relationship("DocumentModel", back_populates="nodes")
    # --- NEW bi-directional edge relationships ---
    outgoing_edges = relationship(
        "EdgeModel",
        foreign_keys="EdgeModel.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan",
    )
    incoming_edges = relationship(
        "EdgeModel",
        foreign_keys="EdgeModel.target_node_id",
        back_populates="target_node",
        cascade="all, delete-orphan",
    )
    # --- NEW user state relationship ---
    user_states = relationship(
        "UserNodeStateModel", back_populates="node", cascade="all, delete-orphan"
    )

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
    # --- NEW fields for #76 schema ---
    relation_type = Column(String, nullable=True)
    strength = Column(Float, nullable=True)

    # --- NEW bi-directional node relationships ---
    source_node = relationship(
        "NodeModel", foreign_keys=[source_node_id], back_populates="outgoing_edges"
    )
    target_node = relationship(
        "NodeModel", foreign_keys=[target_node_id], back_populates="incoming_edges"
    )
    document = relationship("DocumentModel", back_populates="edges")

    def to_domain(self) -> Edge:
        return Edge(
            id=self.id,
            source_id=self.source_node_id,
            target_id=self.target_node_id,
            relation=self.relation_type or "",
        )


class QuizModel(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    # --- NEW fields for #76 schema ---
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=True)
    total_questions = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("DocumentModel", back_populates="quizzes")
    questions = relationship("QuizQuestionModel", back_populates="quiz", cascade="all, delete-orphan")
    # --- NEW relationship ---
    attempts = relationship("QuizAttemptModel", back_populates="quiz", cascade="all, delete-orphan")

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
    # --- NEW field for #76 schema ---
    explanation = Column(Text, nullable=True)

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


# ============================ NEW MODELS #76 ============================

class QuizAttemptModel(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    score = Column(Integer, nullable=False, default=0)
    total = Column(Integer, nullable=False, default=0)
    answers_json = Column(Text, nullable=False, default="{}")
    completed_at = Column(DateTime(timezone=True), server_default=func.now())

    quiz = relationship("QuizModel", back_populates="attempts")


class UserNodeStateModel(Base):
    __tablename__ = "user_node_states"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("nodes.id"), nullable=False)
    state = Column(String, nullable=False, default="new")
    last_reviewed = Column(DateTime(timezone=True), nullable=True)
    review_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    node = relationship("NodeModel", back_populates="user_states")


class ScoreModel(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    correct_count = Column(Integer, nullable=False, default=0)
    total_count = Column(Integer, nullable=False, default=0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("DocumentModel", back_populates="scores")
    quiz = relationship("QuizModel")
