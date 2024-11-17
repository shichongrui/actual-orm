from dataclasses import dataclass
from typing import Annotated, TypedDict
from actual_orm.model import Model
from actual_orm.indexes import UniqueIndex
import actual_orm.db as db
from .owner import Owner
from .content import Content

class Create(TypedDict):
    owner_id: str
    content_id: str

class Update(TypedDict, total=False):
    owner_id: str
    content_id: str

@dataclass
class ContentOwnerAssociation(Model[Create, Update]):
    __table_name__ = "content_owners"

    __indexes__ = [
        UniqueIndex(columns=['content_id', 'owner_id'])
    ]

    id: Annotated[int, db.primary_key(), db.auto_increment()]
    owner_id: Annotated[int, db.foreign_key(Owner)]
    content_id: Annotated[int, db.foreign_key(Content)]
