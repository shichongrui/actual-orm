from typing import List, Optional, Tuple
from dataclasses import dataclass
from .schema import Table, Column, Constraint, Enum
from .action import TableAction, EnumAction

def get_schema_diff_actions(model_schema: Tuple[List[Table], List[Enum]], database_schema: Tuple[List[Table], List[Enum]]):
    actions = []

    model_tables, model_enums = model_schema
    database_tables, database_enums = database_schema

    for model_enum in model_enums:
        if model_enum.name not in [enum.name for enum in database_enums]:
            actions.append(EnumAction(type="CREATE_ENUM", enum=model_enum))

    for database_enum in database_enums:
        if database_enum.name not in [enum.name for enum in model_enums]:
            actions.append(EnumAction(type="DROP_ENUM", enum=database_enum))

    for enum in model_enums:
        database_enum = next((database_enum for database_enum in database_enums if database_enum.name == enum.name), None)

        if database_enum == None:
            continue

        for value in enum.values:
            if value not in database_enum.values:
                actions.append(EnumAction(type="ADD_ENUM_VALUE", enum=database_enum, value=value))


    # Then look for tables that exist in the model_schema that are not in the database_schema and thus
    # need to be created
    for model_table in model_tables:
        if model_table.name not in [table.name for table in database_tables]:
            actions.append(TableAction(type="CREATE_TABLE", table=model_table))
            # Find indexes that don't exist in the database
            for index in model_table.indexes:
                actions.append(TableAction(type="CREATE_INDEX", table=model_table, index=index))
            
            for column in model_table.columns:
                for constraint in column.constraints:
                    actions.append(TableAction(type="ADD_CONSTRAINT", table=model_table, column=column, constraint=constraint))
    
    # Look to see if any tables exist in the database_tables that do not exist in the model_tables
    # And thus need to be dropped
    for db_table in database_tables:
        if db_table.name not in [table.name for table in model_tables]:
            actions.append(TableAction(type="DROP_TABLE", table=db_table))


    for table in model_tables:
        database_table = next(
            (t for t in database_tables if t.name == table.name), None
        )
        if database_table is None:
            continue

        # Find indexes that don't exist in the database
        for index in table.indexes:
            database_index = next((i for i in database_table.indexes if i == index), None)
            if database_index == None:
                actions.append(TableAction(type="CREATE_INDEX", table=table, index=index))

        for db_index in database_table.indexes:
            model_index = next((i for i in table.indexes if i == db_index), None)
            if model_index == None:
                actions.append(TableAction(type="DROP_INDEX", table=database_table, index=db_index))

        # Find columns that exist in the database but do not exist in the model schema anymore
        for db_column in database_table.columns:
            if db_column.name not in [column.name for column in table.columns]:
                actions.append(
                    TableAction(type="DROP_COLUMN", table=db_table, column=db_column)
                )

        # Find columns that exist in the model schema but do not exist in the database schema
        for model_column in table.columns:
            if model_column.name not in [
                column.name for column in database_table.columns
            ]:
                actions.append(
                    TableAction(type="CREATE_COLUMN", table=table, column=model_column)
                )

                for constraint in model_column.constraints:
                    actions.append(TableAction(type="ADD_CONSTRAINT", table=table, column=model_column, constraint=constraint))

        # Figure out how a column changed from what is in the DB
        for column in table.columns:
            database_column = next(
                (c for c in database_table.columns if c.name == column.name), None
            )
            if database_column == None:
                continue

            if column.data_type != database_column.data_type:
                actions.append(
                    TableAction(type="CHANGE_DATA_TYPE", table=table, column=column)
                )

            if (column.default or "").lower() != (database_column.default or "").lower():
                actions.append(
                    TableAction(type="COLUMN_DEFAULT", table=table, column=column)
                )

            if column.nullable == True and database_column.nullable == False:
                actions.append(
                    TableAction(type="COLUMN_NULLABLE", table=table, column=column)
                )

            if column.nullable == False and database_column.nullable == True:
                actions.append(
                    TableAction(type="COLUMN_NOT_NULLABLE", table=table, column=column)
                )

            for constraint in column.constraints:
                database_constraint = next((c for c in database_column.constraints if c.__class__ == constraint.__class__), None)

                if database_constraint == None:
                    actions.append(TableAction(type="ADD_CONSTRAINT", table=table, column=column, constraint=constraint))

            for constraint in database_column.constraints:
                model_constraint = next((c for c in column.constraints if c.__class__ == constraint.__class__), None)
                if model_constraint == None:
                    actions.append(TableAction(type="DROP_CONSTRAINT", table=table, column=column, constraint=constraint))

            for constraint in column.constraints:
                database_constraint = next((c for c in database_column.constraints if c.__class__ == constraint.__class__), None)
                if database_constraint == None:
                    continue

                if constraint != database_constraint:
                    actions.append(TableAction(type="DROP_CONSTRAINT", table=table, column=column, constraint=database_constraint))
                    actions.append(TableAction(type="ADD_CONSTRAINT", table=table, column=column, constraint=constraint))

    return actions
