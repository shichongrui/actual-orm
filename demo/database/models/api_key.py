from typing import Annotated, TypedDict, Optional
from dataclasses import dataclass, field
from actual_orm.model import Model
import actual_orm.indexes as indexes
import actual_orm.db as db
from datetime import datetime
from .application import Application

class Create(TypedDict, total=False):
    key: str
    active: bool
    application_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class Update(TypedDict, total=False):
    key: str
    active: bool
    application_id: int
    created_at: datetime
    updated_at: datetime


@dataclass
class ApiKey(Model[Create, Update]):
    __table_name__ = 'api_keys'
    __indexes__ = [
        indexes.Index(["key", "created_at"]),
        indexes.UniqueIndex(["created_at", "key"])
    ]

    id: Annotated[int, db.primary_key(), db.auto_increment()]
    key: Annotated[str, db.unique(), db.data_types.uuid()]
    active: bool
    application_id: Annotated[int, db.foreign_key(references=Application)]
    created_at: Annotated[datetime, db.default(db.now())]
    updated_at: Annotated[datetime, db.default(db.now())]
    
    # application: Mapped["Application"] = relationship(back_populates="api_keys")
