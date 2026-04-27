"""Document repository — full CRUD."""

from typing import List, Optional

from app.database.models import DocumentModel
from app.dto.documents import CreateDocumentRequest
from app.entities.document import Document
from app.repositories.base_repository import BaseRepository
from sqlalchemy.orm import Session


class DocumentRepository(BaseRepository):
    """CRUD repository for Document entities."""

    _model_cls = DocumentModel

    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_domain(self, model: DocumentModel) -> Document:
        return Document(
            id=model.id,
            title=model.title,
            source_path=model.source_path or "",
            file_path=model.path,
            raw_text=model.raw_text,
            status=model.status,
            error_msg=model.error_msg,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, domain: Document) -> DocumentModel:
        return DocumentModel(
            id=domain.id,
            title=domain.title,
            source_path=domain.source_path,
            path=domain.file_path,
            raw_text=domain.raw_text,
            status=domain.status,
            error_msg=domain.error_msg,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )

    def get_by_id(self, doc_id: int) -> Optional[Document]:
        model = self._db.query(DocumentModel).filter_by(id=doc_id).first()
        return self._to_domain(model) if model else None

    def list_all(self, limit: int = 50, offset: int = 0) -> List[Document]:
        rows = (
            self._db.query(DocumentModel)
            .order_by(DocumentModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def list_by_status(
        self, status: str, limit: int = 50, offset: int = 0
    ) -> List[Document]:
        rows = (
            self._db.query(DocumentModel)
            .filter_by(status=status)
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_domain(r) for r in rows]

    def create(self, data: CreateDocumentRequest) -> Document:
        model = DocumentModel(
            title=data.title,
            path=data.file_path,
            source_path=data.file_path,
            status="pending",
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def create_from_entity(self, domain: Document) -> Document:
        return super().create(domain)

    def update_status(
        self, doc_id: int, status: str, error_msg: str | None = None
    ) -> Optional[Document]:
        model = self._db.query(DocumentModel).filter_by(id=doc_id).first()
        if not model:
            return None
        model.status = status
        if error_msg is not None:
            model.error_msg = error_msg
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def delete(self, doc_id: int) -> bool:
        model = self._db.query(DocumentModel).filter_by(id=doc_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
