from sqlalchemy import Column, Integer, String, Text, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class DocumentModel(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    file_path = Column(String, nullable=True)


class NodeModel(Base):
    __tablename__ = "nodes"
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"))


class EdgeModel(Base):
    __tablename__ = "edges"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, nullable=False)
    target_id = Column(Integer, nullable=False)
    relation = Column(String, nullable=False)


class QuizModel(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
