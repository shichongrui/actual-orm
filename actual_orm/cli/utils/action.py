from typing import Optional
from dataclasses import dataclass
from .schema import (
    Table,
    Column,
    Constraint,
    ForeignKeyConstraint,
    UniqueConstraint,
    Index,
    Enum,
)

@dataclass
class EnumAction:
    type: str

    enum: Enum
    value: Optional[str] = None

@dataclass
class TableAction:
    type: str

    table: Table
    index: Optional[Index] = None
    column: Optional[Column] = None
    constraint: Optional[Constraint] = None


def create_column_sql(column: Column):
    foreign_key_constraint = next(
        (
            constraint
            for constraint in column.constraints
            if isinstance(constraint, ForeignKeyConstraint)
        ),
        None,
    )
    is_unique = next(
        (
            constraint
            for constraint in column.constraints
            if isinstance(constraint, UniqueConstraint)
        ),
        None,
    )
    return (
        f"{column.name}"
        + (f" {column.data_type}" if column.auto_increment == False else " SERIAL")
        + (" NOT NULL" if not column.nullable and not column.primary_key else "")
        + (" PRIMARY KEY" if column.primary_key else "")
        + (f" DEFAULT {column.default}" if column.default else "")
    )


def action_to_sql(action: TableAction | EnumAction) -> str | None:
    if isinstance(action, EnumAction):
        match action.type:
            case "CREATE_ENUM":
                values_sql = ", ".join([f"'{value}'" for value in action.enum.values])
                return f"CREATE TYPE {action.enum.name} AS ENUM ({values_sql})"
            case "DROP_ENUM":
                return f"DROP TYPE {action.enum.name}"
            case "ADD_ENUM_VALUE":
                return f"ALTER TYPE {action.enum.name} ADD VALUE '{action.value}'"


    if isinstance(action, TableAction):
        match action.type:
            case "DROP_TABLE":
                return f"DROP TABLE {action.table.name}"
            case "CREATE_TABLE":
                columns_sql = ", ".join(
                    [create_column_sql(column) for column in action.table.columns]
                )
                return f"CREATE TABLE {action.table.name} ({columns_sql})"
            case "CREATE_INDEX":
                if action.index == None:
                    raise Exception("Index was not provided on the action")
                return f"CREATE{" UNIQUE" if action.index.type == 'unique' else ""} INDEX {action.index.name} ON {action.table.name} ({",".join(action.index.columns)})"
            case "DROP_INDEX":
                if action.index == None:
                    raise Exception("Index was not provided on the action")
                
                return f"DROP INDEX {action.index.name}"
            case "DROP_COLUMN":
                if action.column == None:
                    raise Exception("Column was not provided on the action")
                return f"ALTER TABLE {action.table.name} DROP COLUMN {action.column.name}"
            case "CREATE_COLUMN":
                if action.column == None:
                    raise Exception("Column was not provided on the action")
                return f"ALTER TABLE {action.table.name} ADD COLUMN {create_column_sql(action.column)}"
            case "CHANGE_DATA_TYPE":
                if action.column == None:
                    raise Exception("Column was not provided on the action")
                old_column_sql = f"ALTER TABLE {action.table.name} ALTER COLUMN {action.column.name} TYPE {action.column.data_type}"
                if action.column.data_type == "uuid":
                    old_column_sql += f" USING {action.column.name}::uuid"
                return old_column_sql
            case "COLUMN_NULLABLE":
                if action.column == None:
                    raise Exception("Column was not provided on the action")
                return f"ALTER TABLE {action.table.name} ALTER COLUMN {action.column.name} DROP NOT NULL"

            case "COLUMN_NOT_NULLABLE":
                if action.column == None:
                    raise Exception("Column was not provided on the action")
                return f"ALTER TABLE {action.table.name} ALTER COLUMN {action.column.name} SET NOT NULL"
            case "COLUMN_DEFAULT":
                if action.column == None:
                    raise Exception("Column was not provided on the action")
                if action.column.default == None:
                    return f"ALTER TABLE {action.table.name} ALTER COLUMN {action.column.name} DROP DEFAULT"
                else:
                    return f"ALTER TABLE {action.table.name} ALTER COLUMN {action.column.name} SET DEFAULT {action.column.default}"
            case "ADD_CONSTRAINT":
                if action.column == None:
                    raise Exception("Column was not provided on the action")
                if isinstance(action.constraint, ForeignKeyConstraint):
                    sql = f"ALTER TABLE {action.table.name} ADD CONSTRAINT fk_{action.table.name}_{action.column.name} FOREIGN KEY ({action.column.name}) REFERENCES {action.constraint.references}"
                    if action.constraint.on_delete != None:
                        sql += f" ON DELETE {action.constraint.on_delete}"
                    return sql
                elif isinstance(action.constraint, UniqueConstraint):
                    return f"ALTER TABLE {action.table.name} ADD CONSTRAINT uq_{action.table.name}_{action.column.name} UNIQUE ({action.column.name})"
            case "DROP_CONSTRAINT":
                if action.column == None:
                    raise Exception("Column was not provided on the action")
                if isinstance(action.constraint, ForeignKeyConstraint):
                    return f"ALTER TABLE {action.table.name} DROP CONSTRAINT fk_{action.table.name}_{action.column.name}"
                elif isinstance(action.constraint, UniqueConstraint):
                    return f"ALTER TABLE {action.table.name} DROP CONSTRAINT uq_{action.table.name}_{action.column.name}"
            case _:
                raise ValueError(f"Unknown Action type: {action.type}")
