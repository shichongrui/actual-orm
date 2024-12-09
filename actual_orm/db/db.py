from typing import Callable, TypedDict, get_origin, get_args, Annotated, Dict
from enum import StrEnum, auto
from dataclasses import field, fields
# from .func import now, current_timestamp
from actual_orm.model import Model
from . import data_types

def primary_key():
    return {"primary_key": True}

def auto_increment():
    return {
        "auto_increment": True,
        **data_types.serial(),
    }

def now():
    return "NOW()"

def random():
    return "RANDOM()"

def default(value: str):
    return {
        "default": value
    }

def updated_at():
    return {
        "updated_at": True
    }

def cascade():
    return { "on_delete": "CASCADE" }

def foreign_key(references: type[Model], on_delete: Dict | None = None):
    primary_key = next((column_name for column_name, type in references.__annotations__.items() if get_origin(type) is Annotated and {"primary_key": True} in get_args(type)), None)
    if primary_key is None:
        raise Exception(f"No primary key found on table {references.__class__.__name__}")
    return {
        "foreign_key": {
            "key": f"{references.__table_name__}({primary_key})",
            **(on_delete or {})
        }
    }

def unique():
    return {"unique": True}