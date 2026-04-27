from app.database.connection import TEST_DB_URL, DatabaseConnection
from app.database.models import (
    DocumentModel,
    EdgeModel,
    NodeModel,
    QuizModel,
    QuizQuestionModel,
)
from sqlalchemy.orm import Session


def test_document_model_basic():
    conn = DatabaseConnection(TEST_DB_URL)
    from app.database.models import Base

    conn.create_tables(Base)
    session = next(conn.get_session())
    doc = DocumentModel(title="Hello", path="/tmp/test.pdf")
    session.add(doc)
    session.commit()
    assert doc.id is not None
    assert doc.title == "Hello"
    session.close()


class TestDatabaseConnection:
    def test_get_session_and_commit(self):
        from app.database.models import Base

        conn = DatabaseConnection(TEST_DB_URL)
        conn.create_tables(Base)
        session = next(conn.get_session())
        doc = DocumentModel(title="Fixture doc")
        session.add(doc)
        session.commit()
        assert doc.id is not None
        session.close()
