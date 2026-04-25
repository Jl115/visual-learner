from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas import document as doc_schema
from app.models import Document
from app.schemas.document import DocumentOut
import fitz
from datetime import datetime

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
    return doc

@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.id == doc_id).first()
