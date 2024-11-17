from dataclasses import dataclass
from typing import List, Any

@dataclass
class ModelColumn:
    table: str
    name: str

    def in_(self, values: List[Any]):
        from .conditions import Condition
        return Condition(column=self, condition="in", value=values)

    def __lt__(self, other):
        from .conditions import Condition
        return Condition(column=self, condition="<", value=other)

    def __gt__(self, other):
        from .conditions import Condition
        return Condition(column=self, condition=">", value=other)

    def __eq__(self, other):
        from .conditions import Condition
        return Condition(column=self, condition="=", value=other)