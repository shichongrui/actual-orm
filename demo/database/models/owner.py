from typing import Annotated, TypedDict, Optional
from datetime import datetime
from dataclasses import dataclass
from actual_orm.model import Model
from actual_orm.indexes import UniqueIndex
import actual_orm.db as db
from .application import Application

class Create(TypedDict, total=False):
    external_id: str
    application_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class Update(TypedDict, total=False):
    external_id: str
    application_id: int
    created_at: datetime
    updated_at: datetime

@dataclass
class Owner(Model[Create, Update]):
    __table_name__ = "owners"
    __indexes__ = [
        UniqueIndex(["application_id", "external_id"])
    ]

    id: Annotated[int, db.primary_key(), db.auto_increment()]
    external_id: str
    application_id: Annotated[int, db.foreign_key(Application)]
    created_at: Annotated[datetime, db.default(db.now())]
    updated_at: Annotated[datetime, db.default(db.now()), db.updated_at()]

