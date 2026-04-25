import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Document
from app.services.nlp_pipeline import analyze_document
from app.services.graph_builder import build_and_persist_graph, persist_quizzes

async def analyze_doc_background(doc_id: str, raw_text: str):
    """Run the full LLM pipeline asynchronously after Document is saved."""
    # Run the async NLP pipeline (httpx to Ollama)
    result = await analyze_document(doc_id, raw_text)

    # Use a fresh sync DB session for persistence
    db = SessionLocal()
    try:
        themes = result.get("themes", [])
        connections = result.get("connections", [])
        quizzes = result.get("quizzes", {})

        # Fetch the document
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return

        # Build and persist the graph
        from app.services.graph_builder import build_and_persist_graph
        build_and_persist_graph(db, doc, themes, connections)

        # Map theme name to node ID for quizzes
        from app.models import Node
        nodes = db.query(Node).filter(Node.document_id == doc_id).all()
        quiz_payload = {}
        for node in nodes:
            qs = quizzes.get(node.label, [])
            if qs:
                quiz_payload[node.id] = qs

        persist_quizzes(db, doc_id, quiz_payload)
    finally:
        db.close()
