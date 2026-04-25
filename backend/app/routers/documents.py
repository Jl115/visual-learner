from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas import document as doc_schema
from app.models import document, node, edge, quiz
import fitz
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/upload", response_model=doc_schema.DocumentOut)
def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read()
    doc_id = str(uuid.uuid4())

    # Extract text
    fitz_doc = fitz.open(stream=content, filetype="pdf")
    raw_text = ""
    for page in fitz_doc:
        raw_text += page.get_text()
    fitz_doc.close()

    doc = document.Document(
        id=doc_id,
        filename=file.filename,
        raw_text=raw_text,
        created_at=datetime.utcnow(),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@router.get("/{doc_id}", response_model=doc_schema.DocumentOut)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    return db.query(document.Document).filter(document.Document.id == doc_id).first()
