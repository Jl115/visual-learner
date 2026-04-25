from sqlalchemy import Column, String, Text, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, nullable=False)
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    
    nodes = relationship("Node", back_populates="document")
    edges = relationship("Edge", back_populates="document")
    quizzes = relationship("Quiz", back_populates="document")

class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"))
    node_id = Column(String, ForeignKey("nodes.id"))
    question = Column(Text, nullable=False)
    options = Column(Text)  # JSON string
    correct_index = Column(Integer, nullable=False)

    document = relationship("Document", back_populates="quizzes")
    node = relationship("Node", back_populates="quizzes")

class Node(Base):
    __tablename__ = "nodes"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"))
    label = Column(String, nullable=False)
    summary = Column(Text)
    weight = Column(Integer, default=1)
    color = Column(String)
    x = Column(Float)
    y = Column(Float)

    document = relationship("Document", back_populates="nodes")
    quizzes = relationship("Quiz", back_populates="node")

class Edge(Base):
    __tablename__ = "edges"

    id = Column(String, primary_key=True, default=generate_uuid)
    document_id = Column(String, ForeignKey("documents.id"))
    source_id = Column(String, ForeignKey("nodes.id"))
    target_id = Column(String, ForeignKey("nodes.id"))
    weight = Column(Float, default=1.0)

    document = relationship("Document", back_populates="edges")
