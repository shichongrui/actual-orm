from typing import Annotated, Optional, TypedDict
from dataclasses import dataclass, field
from actual_orm.model import Model
import actual_orm.db as db
from datetime import datetime

class Create(TypedDict, total=False):
    external_id: str
    title: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class Update(TypedDict, total=False):
    external_id: str
    title: str
    created_at: datetime
    updated_at: datetime

@dataclass
class Application(Model[Create, Update]):
    __table_name__ = 'applications'

    id: Annotated[int, db.primary_key(), db.auto_increment()]
    external_id: str
    title: str
    created_at: Annotated[datetime, db.default(db.now())]
    updated_at: Annotated[datetime, db.default(db.now()), db.updated_at()]
