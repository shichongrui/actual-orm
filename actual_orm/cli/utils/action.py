from typing import Optional
from dataclasses import dataclass
from .schema import (
    Table,
    Column,
    Constraint,
    ForeignKeyConstraint,
    UniqueConstraint,
    Index,
)


@dataclass
class Action:
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
        + (f" UNIQUE" if is_unique else "")
        + (
            f" REFERENCES {foreign_key_constraint.references}"
            if foreign_key_constraint
            else ""
        )
    )


def action_to_sql(action: Action) -> str:
    match action.type:
        case "DROP_TABLE":
            return f"DROP TABLE {action.table.name}"
        case "CREATE_TABLE":
            columns_sql = ", ".join(
                [create_column_sql(column) for column in action.table.columns]
            )
            return f"CREATE TABLE {action.table.name} ({columns_sql})"
        case "CREATE_INDEX":
            return f"CREATE{" UNIQUE" if action.index.type == 'unique' else ""} INDEX {action.index.name} ON {action.table.name} ({",".join(action.index.columns)})"
        case "DROP_INDEX":
            return f"DROP INDEX {action.index.name}"
        case "DROP_COLUMN":
            return f"ALTER TABLE {action.table.name} DROP COLUMN {action.column.name}"
        case "CREATE_COLUMN":
            return f"ALTER TABLE {action.table.name} ADD COLUMN {create_column_sql(action.column)}"
        case "CHANGE_DATA_TYPE":
            old_column_sql = f"ALTER TABLE {action.table.name} ALTER COLUMN {action.column.name} TYPE {action.column.data_type}"
            if action.column.data_type == "uuid":
                old_column_sql += f" USING {action.column.name}::uuid"
            return old_column_sql
        case "COLUMN_NULLABLE":
            return f"ALTER TABLE {action.table.name} ALTER COLUMN {action.column.name} DROP NOT NULL"

        case "COLUMN_NOT_NULLABLE":
            return f"ALTER TABLE {action.table.name} ALTER COLUMN {action.column.name} SET NOT NULL"
        case "COLUMN_DEFAULT":
            if action.column.default == None:
                return f"ALTER TABLE {action.table.name} ALTER COLUMN {action.column.name} DROP DEFAULT"
            else:
                return f"ALTER TABLE {action.table.name} ALTER COLUMN {action.column.name} SET DEFAULT {action.column.default}"
        case "ADD_CONSTRAINT":
            if isinstance(action.constraint, ForeignKeyConstraint):
                return f"ALTER TABLE {action.table.name} ADD CONSTRAINT fk_{action.column.name} FOREIGN KEY ({action.column.name}) REFERENCES {action.constraint.references}"
            elif isinstance(action.constraint, UniqueConstraint):
                return f"ALTER TABLE {action.table.name} ADD CONSTRAINT uq_{action.column.name} UNIQUE ({action.column.name})"
        case "DROP_CONSTRAINT":
            if isinstance(action.constraint, ForeignKeyConstraint):
                return f"ALTER TABLE {action.table.name} DROP CONSTRAINT fk_{action.column.name}"
            elif isinstance(action.constraint, UniqueConstraint):
                return f"ALTER TABLE {action.table.name} DROP CONSTRAINT uq_{action.column.name}"
        case _:
            raise ValueError(f"Unknown Action type: {action.type}")
