"""SQLAlchemy ORM models for VisualLearner."""
from datetime import datetime
from sqlalchemy import (
    Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint,
    func, event, Index,
)
from sqlalchemy.orm import declarative_base, relationship
import uuid

# SQLite-compatible UUID type
def _generate_uuid():
    return str(uuid.uuid4())

Base = declarative_base()


class DocumentModel(Base):
    __tablename__ = "documents"
    __table_args__ = (Index("idx_documents_status", "status"),)

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    title = Column(Text, nullable=False, default="")
    source_path = Column(Text, nullable=False, default="")
    raw_text = Column(Text, nullable=True)
    status = Column(Text, nullable=False, default="pending")
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    nodes = relationship("NodeModel", back_populates="document", cascade="all, delete-orphan")
    edges = relationship("EdgeModel", back_populates="document", cascade="all, delete-orphan")
    quizzes = relationship("QuizModel", back_populates="document", cascade="all, delete-orphan")
    scores = relationship("ScoreModel", back_populates="document", cascade="all, delete-orphan")


class NodeModel(Base):
    __tablename__ = "nodes"
    __table_args__ = (Index("idx_nodes_document_id", "document_id"),)

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    label = Column(Text, nullable=False, default="")
    summary = Column(Text, nullable=False, default="")
    full_text = Column(Text, nullable=False, default="")
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    color = Column(Text, nullable=False, default="#4ECDC4")
    weight = Column(Float, nullable=False, default=0.0)
    theme_category = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    document = relationship("DocumentModel", back_populates="nodes")
    outgoing_edges = relationship("EdgeModel", foreign_keys="EdgeModel.source_node_id", back_populates="source_node", cascade="all, delete-orphan")
    incoming_edges = relationship("EdgeModel", foreign_keys="EdgeModel.target_node_id", back_populates="target_node", cascade="all, delete-orphan")
    user_states = relationship("UserNodeStateModel", back_populates="node", cascade="all, delete-orphan")


class EdgeModel(Base):
    __tablename__ = "edges"
    __table_args__ = (
        Index("idx_edges_document_id", "document_id"),
        Index("idx_edges_source", "source_node_id"),
        Index("idx_edges_target", "target_node_id"),
    )

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    source_node_id = Column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    target_node_id = Column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    relation_type = Column(Text, nullable=True)
    strength = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    source_node = relationship("NodeModel", foreign_keys=[source_node_id], back_populates="outgoing_edges")
    target_node = relationship("NodeModel", foreign_keys=[target_node_id], back_populates="incoming_edges")
    document = relationship("DocumentModel", back_populates="edges")


class QuizModel(Base):
    __tablename__ = "quizzes"
    __table_args__ = (Index("idx_quizzes_document_id", "document_id"),)

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    node_id = Column(String(36), ForeignKey("nodes.id", ondelete="SET NULL"), nullable=True)
    total_questions = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    document = relationship("DocumentModel", back_populates="quizzes")
    node = relationship("NodeModel")
    questions = relationship("QuizQuestionModel", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttemptModel", back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestionModel(Base):
    __tablename__ = "quiz_questions"
    __table_args__ = (Index("idx_quiz_questions_quiz_id", "quiz_id"),)

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    quiz_id = Column(String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False, default="")
    options_json = Column(Text, nullable=False, default="[]")
    correct_index = Column(Integer, nullable=False, default=0)
    explanation = Column(Text, nullable=True)

    # Relationships
    quiz = relationship("QuizModel", back_populates="questions")


class QuizAttemptModel(Base):
    __tablename__ = "quiz_attempts"
    __table_args__ = (Index("idx_quiz_attempts_quiz_id", "quiz_id"),)

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    quiz_id = Column(String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    score = Column(Integer, nullable=False, default=0)
    total = Column(Integer, nullable=False, default=0)
    answers_json = Column(Text, nullable=False, default="{}")
    completed_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    quiz = relationship("QuizModel", back_populates="attempts")


class UserNodeStateModel(Base):
    __tablename__ = "user_node_states"
    __table_args__ = (Index("idx_user_node_states_node_id", "node_id"),)

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    node_id = Column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    state = Column(Text, nullable=False, default="new")
    last_reviewed = Column(DateTime(timezone=True), nullable=True)
    review_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    node = relationship("NodeModel", back_populates="user_states")


class ScoreModel(Base):
    __tablename__ = "scores"
    __table_args__ = (
        Index("idx_scores_document_id", "document_id"),
        Index("idx_scores_quiz_id", "quiz_id"),
    )

    id = Column(String(36), primary_key=True, default=_generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    quiz_id = Column(String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    correct_count = Column(Integer, nullable=False, default=0)
    total_count = Column(Integer, nullable=False, default=0)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    document = relationship("DocumentModel", back_populates="scores")
    quiz = relationship("QuizModel")
