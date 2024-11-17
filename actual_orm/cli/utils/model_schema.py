from typing import (
    Type,
    Any,
    get_origin,
    Union,
    get_args,
    Annotated,
    Dict,
)
from dataclasses import dataclass
from .to_snake_case import to_snake_case
from .schema import Table, Column, ForeignKeyConstraint, UniqueConstraint, Index
from ...model import Model

DATA_TYPE_LOOKUP = {
    "str": "text",
    "int": "int4",
    "bool": "bool",
    "float": "double precision",
    "datetime": "timestamptz(3)",
    "dict": "jsonb",
    "list": "jsonb"
}


def is_optional(type_hint):
    origin = get_origin(type_hint)  # Get the origin of the type (e.g., Union)
    return origin is Union and None.__class__ in get_args(type_hint)


class ColumnDataTypeNotCompatible(Exception):
    def __init__(self, name: str, model_name: str):
        self.name = name

        super().__init__(f"The type for {name} on model {model_name} is incompatible.")


def get_column_type(type):
    origin = get_origin(type)
    if origin is Union:
        type_name = [type for type in get_args(type) if type is not None][0]
        type = DATA_TYPE_LOOKUP[type_name.__name__]
    else:
        type = DATA_TYPE_LOOKUP[type.__name__]

    if type == None:
        raise
    return type


def get_table_name(model: Type[Model]):
    return model.__table_name__ or to_snake_case(model.__name__)


def get_model_schema(model: Type[Model]):
    columns = []
    for column_name, type in model.__annotations__.items():
        is_annotated = get_origin(type) is Annotated
        data_type = type
        meta_data: Dict[str, Any] = {}
        if is_annotated:
            data_type, *annotations = get_args(type)
            meta_data["data_type"] = get_column_type(data_type)
            for annotation in annotations:
                meta_data.update(annotation)
            meta_data["nullable"] = is_optional(data_type) and "default" not in meta_data and "primary_key" not in meta_data and "auto_increment" not in meta_data
        else:
            meta_data["data_type"] = get_column_type(data_type)
            meta_data["nullable"] = is_optional(data_type)

        constraints = []
        foreign_key = meta_data.get("foreign_key")
        unique: bool = meta_data.get("unique", False)
        if isinstance(foreign_key, str):
            constraints.append(ForeignKeyConstraint(references=foreign_key))
        if unique:
            constraints.append(UniqueConstraint())

        columns.append(
            Column(
                name=column_name,
                data_type=meta_data.get("data_type", ""),
                nullable=meta_data.get("nullable", False),
                primary_key=meta_data.get("primary_key", False),
                auto_increment=meta_data.get("auto_increment", False),
                default=meta_data.get("default", None),
                constraints=constraints,
            )
        )
    
    indexes = []
    for index in model.__indexes__:
        indexes.append(Index(
            name=f"idx_{get_table_name(model)}_{index.type}_{"_".join([column for column in index.columns])}",
            type=index.type,
            columns=index.columns
        ))

    table = Table(name=get_table_name(model), columns=columns, indexes=indexes)
    return table
