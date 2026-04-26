from typing import Optional, List
from app.domains.document import Document


class DocumentRepo:
    def get(self, id: int) -> Optional[Document]:
        raise NotImplementedError

    def list(self) -> List[Document]:
        raise NotImplementedError

    def create(self, document: Document) -> Document:
        raise NotImplementedError
