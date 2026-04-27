"""Base repository with generic CRUD using SQLAlchemy."""

from typing import Generic, List, Optional, TypeVar

from sqlalchemy.orm import Session

Domain = TypeVar("Domain")
Model = TypeVar("Model")


class BaseRepository(Generic[Model, Domain]):
    """Abstract base repository defining the generic CRUD interface.

    Subclasses must provide:
      - _model_cls: SQLAlchemy model class
      - _to_domain(model): convert SQLAlchemy model -> domain dataclass
      - _to_model(domain): convert domain dataclass -> SQLAlchemy model
    """

    _model_cls: type[Model]

    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_domain(self, model: Model) -> Domain:
        raise NotImplementedError

    def _to_model(self, domain: Domain) -> Model:
        raise NotImplementedError

    def get_by_id(self, _id: int) -> Optional[Domain]:
        model = self._db.query(self._model_cls).filter_by(id=_id).first()
        return self._to_domain(model) if model else None

    def list_all(self, limit: int = 50, offset: int = 0) -> List[Domain]:
        rows = self._db.query(self._model_cls).offset(offset).limit(limit).all()
        return [self._to_domain(r) for r in rows]

    def create(self, domain: Domain) -> Domain:
        model = self._to_model(domain)
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def delete(self, _id: int) -> bool:
        model = self._db.query(self._model_cls).filter_by(id=_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True
