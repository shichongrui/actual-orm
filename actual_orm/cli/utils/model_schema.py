from typing import (
    Type,
    List,
    Any,
    get_origin,
    Union,
    get_args,
    Annotated,
    Dict,
)
import os
import sys
import importlib
from enum import StrEnum
from dataclasses import dataclass
from .to_snake_case import to_snake_case
from .schema import Table, Column, ForeignKeyConstraint, UniqueConstraint, Index, Enum
from ...model import Model

DATA_TYPE_LOOKUP = {
    "str": "text",
    "int": "int4",
    "bool": "bool",
    "float": "double precision",
    "datetime": "timestamptz(3)",
    "dict": "jsonb",
    "list": "jsonb",
}

# Add the FastAPI project's root directory to sys.path
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def get_relavent_exports():
    model_files = os.listdir("database/models")

    exports = set()
    for model_file in model_files:
        if model_file.endswith(".py") == False:
            continue

        module = importlib.import_module(
            f"database.models.{model_file.replace(".py", "")}"
        )
        for attribute_name in dir(module):
            export = getattr(module, attribute_name)
            if (
                isinstance(export, type)
                and export != Model
                and (issubclass(export, Model) or issubclass(export, StrEnum))
            ):
                exports.add(export)

    return exports


def enum_name(enum: Type[StrEnum]):
    return to_snake_case(enum.__name__)


def is_optional(type_hint):
    origin = get_origin(type_hint)  # Get the origin of the type (e.g., Union)
    return origin is Union and None.__class__ in get_args(type_hint)


class ColumnDataTypeNotCompatible(Exception):
    def __init__(self, name: str, model_name: str):
        self.name = name

        super().__init__(f"The type for {name} on model {model_name} is incompatible.")


def get_column_type(python_type):
    origin = get_origin(python_type)

    if origin is Union:
        python_type = [type for type in get_args(python_type) if type is not None][0]

    if issubclass(python_type, StrEnum):
        return enum_name(python_type)

    type = DATA_TYPE_LOOKUP[python_type.__name__]

    if type == None:
        raise
    return type


def is_enum_type(python_type):
    origin = get_origin(python_type)
    if origin is Union:
        python_type = next(
            (type for type in get_args(python_type) if type is not None), None
        )

    if python_type is None:
        raise Exception(f"Python type could not be determined")

    if issubclass(python_type, StrEnum):
        return python_type

    return None


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
            meta_data["nullable"] = (
                is_optional(data_type)
                and "default" not in meta_data
                and "primary_key" not in meta_data
                and "auto_increment" not in meta_data
            )
        else:
            meta_data["data_type"] = get_column_type(data_type)
            meta_data["nullable"] = is_optional(data_type)

        constraints = []
        foreign_key = meta_data.get("foreign_key")
        unique: bool = meta_data.get("unique", False)
        if foreign_key != None:
            constraints.append(ForeignKeyConstraint(references=foreign_key.get("key"), on_delete=foreign_key.get("on_delete")))
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
        indexes.append(
            Index(
                name=f"idx_{get_table_name(model)}_{index.type}_{"_".join([column for column in index.columns])}",
                type=index.type,
                columns=index.columns,
            )
        )

    table = Table(name=get_table_name(model), columns=columns, indexes=indexes)
    return table


def get_models_schema():
    exports = get_relavent_exports()

    tables = []
    enums = []
    for export in exports:
        if issubclass(export, Model):
            tables.append(get_model_schema(export))
        elif issubclass(export, StrEnum) and export != StrEnum:
            enums.append(
                Enum(name=enum_name(export), values=[member.value for member in export])
            )

    return tables, enums