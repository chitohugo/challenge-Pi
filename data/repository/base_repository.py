from contextlib import AbstractContextManager
from typing import Callable

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import *


class BaseRepository:
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]], model) -> None:
        self.session_factory = session_factory
        self.model = model

    def _read_by_field(self, field_name, value):
        with self.session_factory() as session:
            query = session.query(self.model)
            query = query.filter(getattr(self.model, field_name) == value).first()
            if not query:
                raise NotFoundError(detail=f"Not found {field_name} : {value}")
            return query

    def read_by_id(self, id: int):
        return self._read_by_field("id", id)

    def read_by_email(self, email: str):
        return self._read_by_field("email", email)

    def read(self):
        with self.session_factory() as session:
            query = session.query(self.model)
            return paginate(session, query)

    def create(self, schema):
        with self.session_factory() as session:
            query = self.model(**schema.dict())
            try:
                session.add(query)
                session.commit()
                session.refresh(query)
            except IntegrityError as e:
                error_msg = str(e.orig)
                field = error_msg.split(".")[1]
                raise DuplicatedError(detail=f"The {field} value already exists")
            return query

    def update(self, id: int, schema):
        with self.session_factory() as session:
            session.query(self.model).filter(self.model.id == id).update(schema.dict(exclude_none=True))
            session.commit()
            return self.read_by_id(id)

    def delete_by_id(self, id: int):
        with self.session_factory() as session:
            query = session.query(self.model).filter(self.model.id == id).first()
            if not query:
                raise NotFoundError(detail=f"not found id : {id}")
            session.delete(query)
            session.commit()
