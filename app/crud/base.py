from typing import Any, Generic, Literal, Optional, TypeVar, Union, get_args
from uuid import UUID

from app import schemas
from app.db.base_class import Base
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import desc
from sqlalchemy.orm import Session
from sqlalchemy.orm.query import Query

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ReturnSchemaType = TypeVar("ReturnSchemaType", bound=BaseModel)


class CRUDBase(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType, ReturnSchemaType]
):
    model: type[ModelType]
    create_schema: type[CreateSchemaType]
    update_schema: type[UpdateSchemaType]
    return_schema: type[ReturnSchemaType]

    def __init__(self) -> None:
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        """
        (
            self.model,
            self.create_schema,
            self.update_schema,
            self.return_schema,
        ) = get_args(
            self.__class__.__orig_bases__[0]  # type: ignore
        )

    def length(self, db: Session) -> int:
        return db.query(self.model).count()

    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session) -> tuple[int, list[ModelType]]:
        query = db.query(self.model)
        return self._filter_multi_query(query)

    def _filter_multi_query(self, query: Query) -> tuple[int, list[ModelType]]:
        query = query.order_by(self.model.created)
        return (query.count(), query.all())

    def create(
        self, db: Session, *, obj_in: CreateSchemaType, commit: bool = True
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in, by_alias=False)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj, by_alias=False)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(
                exclude_unset=True, exclude_defaults=True, by_alias=False
            )
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> Optional[ModelType]:
        obj = db.query(self.model).get(id)
        return obj and self.remove_obj(db, obj=obj)

    def remove_obj(self, db: Session, *, obj: ModelType) -> ModelType:
        db.delete(obj)
        db.commit()
        return obj
