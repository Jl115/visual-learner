from sqlalchemy.orm import Session
from app.database.models import DocumentModel, NodeModel, EdgeModel, QuizModel, QuizQuestionModel
from app.database.connection import DatabaseConnection, TEST_DB_URL


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
