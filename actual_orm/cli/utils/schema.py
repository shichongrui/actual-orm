from typing import List
from dataclasses import dataclass

@dataclass(eq=True)
class Constraint:
    pass

@dataclass(eq=True)
class ForeignKeyConstraint(Constraint):
    references: str
    on_delete: str | None = None

@dataclass(eq=True)
class UniqueConstraint(Constraint):
    pass

@dataclass
class Column:
    name: str
    data_type: str
    primary_key: bool
    auto_increment: bool
    default: str | None
    constraints: List[ForeignKeyConstraint | UniqueConstraint]
    
    nullable: bool = False
    
    
@dataclass(eq=True)
class Index:
    name: str
    type: str
    columns: List[str]

@dataclass
class Table:
    name: str
    columns: List[Column]
    indexes: List[Index]

@dataclass
class Enum:
    name: str
    values: List[str]