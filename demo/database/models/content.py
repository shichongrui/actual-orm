from typing import Annotated, TypedDict, Optional
from enum import StrEnum, auto
from dataclasses import dataclass
from datetime import datetime
from actual_orm.model import Model
import actual_orm.db as db

class Create(TypedDict, total=False):
    id: Optional[int]
    title: str
    external_id: str
    hash: str
    full_text: str
    context_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class Update(TypedDict, total=False):
    title: str
    external_id: str
    hash: str
    full_text: str
    context_id: str
    created_at: datetime
    updated_at: datetime

class ContentType(StrEnum):
    markdown = auto()
    text = auto()
    vtt = auto()
    pdf = auto()

@dataclass
class Content(Model):
    __table_name__ = "content"

    id: Annotated[int, db.primary_key(), db.auto_increment()]
    title: str
    external_id: str
    type: ContentType
    hash: Annotated[str, db.data_types.varchar(64)]
    full_text: str
    context_id: str
    created_at: Annotated[datetime, db.default(db.now())]
    updated_at: Annotated[datetime, db.default(db.now())]

    # owners: Mapped[List["Owner"]] = relationship(
    #     secondary=content_owner_association_table, back_populates="content"
    # )