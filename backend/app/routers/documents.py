from fastapi import APIRouter, Depends, UploadFile, File
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.document import DocumentOut
from app.models import Document
from app.services.task_runner import analyze_doc_background
from app.services.graph_builder import build_and_persist_graph, persist_quizzes
from app.services.nlp_pipeline import analyze_document
import fitz
from datetime import datetime
import asyncio
import threading

router = APIRouter()

@router.post("/upload", response_model=DocumentOut)
def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read()

    # Extract text
    fitz_doc = fitz.open(stream=content, filetype="pdf")
    raw_text = ""
    for page in fitz_doc:
        raw_text += page.get_text()
    fitz_doc.close()

    doc = Document(
        filename=file.filename,
        raw_text=raw_text,
        created_at=datetime.utcnow(),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Kick off background NLP pipeline in a new thread with its own event loop
    def run_analysis():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(analyze_doc_background(doc.id, raw_text))
        loop.close()

    thread = threading.Thread(target=run_analysis, daemon=True)
    thread.start()

    return doc

@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.id == doc_id).first()
