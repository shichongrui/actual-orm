from typing import List
from dataclasses import dataclass

@dataclass
class Index():
    type = 'index'
    columns: List[str]

@dataclass
class UniqueIndex():
    type = 'unique'
    columns: List[str]