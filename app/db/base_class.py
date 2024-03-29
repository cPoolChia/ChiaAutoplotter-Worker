from datetime import datetime

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from fastapi_utils.guid_type import GUID
from sqlalchemy import Column, DateTime
import uuid

# NOTE Fixes a warning
GUID.cache_ok = True  # type: ignore


@as_declarative()
class Base:
    __name__: str

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    created = Column(DateTime, default=datetime.utcnow)

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} object with id={self.id}>"
