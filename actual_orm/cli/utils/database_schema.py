from typing import List, Dict
import asyncpg
from .schema import Table, Column, Index, ForeignKeyConstraint, UniqueConstraint, Enum


async def get_database_schema(database_url):
    conn = await asyncpg.connect(database_url)

    tables: List[Table] = []
    enums: List[Enum] = []

    tables_result = await conn.fetch(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name != '_actual_orm_migrations'
    """
    )

    for table_result in tables_result:
        table_name = table_result["table_name"]

        columns_result = await conn.fetch(
            """
SELECT 
    c.column_name,
    c.udt_name AS data_type,
    c.datetime_precision,
    c.character_maximum_length AS char_length,
    c.is_nullable,
    c.column_default AS default_value,
    COALESCE(pk.constraint_name IS NOT NULL, false) AS is_primary_key,
    COALESCE(s.relname IS NOT NULL AND s.relkind = 'S', false) AS is_auto_increment,
    rcu.table_name as foreign_key_table,
    rcu.column_name as foreign_key_column,
    COALESCE(uc.constraint_name IS NOT NULL, false) AS is_unique_constraint
FROM 
    information_schema.columns c
LEFT JOIN 
    (SELECT kcu.column_name, tc.constraint_name
     FROM 
         information_schema.key_column_usage kcu
     JOIN 
         information_schema.table_constraints tc 
         ON kcu.constraint_name = tc.constraint_name 
         AND kcu.table_schema = tc.table_schema 
     WHERE 
         tc.constraint_type = 'PRIMARY KEY'
    ) pk 
    ON c.column_name = pk.column_name 
    AND c.table_name = $1
LEFT JOIN 
    pg_class s 
    ON c.column_default LIKE '%' || s.relname || '%' 
    AND s.relkind = 'S'
LEFT JOIN 
    information_schema.key_column_usage kcu
    ON c.column_name = kcu.column_name 
    AND c.table_name = kcu.table_name
LEFT JOIN 
    information_schema.referential_constraints rc
    ON kcu.constraint_name = rc.constraint_name
LEFT JOIN 
    information_schema.constraint_column_usage rcu
    ON rc.unique_constraint_name = rcu.constraint_name
    AND kcu.table_schema = rcu.table_schema
LEFT JOIN 
    information_schema.key_column_usage uc_kcu
    ON c.column_name = uc_kcu.column_name
    AND c.table_name = uc_kcu.table_name
LEFT JOIN 
    information_schema.table_constraints uc
    ON uc_kcu.constraint_name = uc.constraint_name
    AND uc.constraint_type = 'UNIQUE'
WHERE 
    c.table_name = $1
AND 
    c.table_schema = 'public';
        """,
            table_name,
        )

        indexes_result = await conn.fetch(r"""
            SELECT
                ix.relname as index_name,
                indisunique as is_unique,
                replace(regexp_replace(regexp_replace(regexp_replace(pg_get_indexdef(indexrelid), ' WHERE .+|INCLUDE .+', ''), ' WITH .+', ''), '.*\((.*)\)', '\1'), ' ', '') AS column_name
            FROM pg_index i 
            JOIN pg_class t ON t.oid = i.indrelid
            JOIN pg_class ix ON ix.oid = i.indexrelid
            JOIN pg_namespace n ON t.relnamespace = n.oid
            WHERE t.relname = $1
                AND n.nspname = 'public';
        """, table_name)

        columns = []
        for column_result in columns_result:
            data_type = column_result['data_type']
            if data_type == 'timestamptz':
                data_type = f'timestamptz({column_result.get('datetime_precision', 3)})'
            if data_type == 'varchar':
                data_type = f'varchar({column_result.get('char_length', 1)})'
            if column_result['is_auto_increment']:
                data_type = 'serial'

            constraints = []
            if column_result['foreign_key_table'] is not None and column_result['foreign_key_column'] is not None:
                constraints.append(ForeignKeyConstraint(references=f"{column_result["foreign_key_table"]}({column_result["foreign_key_column"]})"))

            if column_result['is_unique_constraint']:
                constraints.append(UniqueConstraint())

            column = Column(
                name=column_result["column_name"],
                data_type=data_type,
                nullable=column_result["is_nullable"] == "YES",
                primary_key=column_result["is_primary_key"],
                auto_increment=column_result["is_auto_increment"],
                default=(
                    column_result["default_value"]
                    if column_result["is_auto_increment"] == False
                    else None
                ),
                constraints=constraints
            )

            columns.append(column)
        
        indexes = []
        for index in indexes_result:
            if index.get('index_name', "").startswith("idx_") == False:
                continue
            indexes.append(
                Index(
                    name=index.get('index_name'),
                    type="unique" if index.get('is_unique') else "index",
                    columns=index.get("column_name", "").split(',')
                )
            )

        tables.append(Table(name=table_name, columns=columns, indexes=indexes))

    enums_result = await conn.fetch("""
        SELECT
            n.nspname AS schema_name,
            t.typname AS enum_name,
            e.enumlabel AS enum_value
        FROM
            pg_type t
        JOIN
            pg_enum e ON t.oid = e.enumtypid
        JOIN
            pg_namespace n ON t.typnamespace = n.oid
        ORDER BY
            schema_name, enum_name, e.enumsortorder;                             
    """)
    enums_lookup: Dict[str, Enum] = {}
    for result in enums_result:
        enum = enums_lookup.get(result['enum_name'], Enum(name=result['enum_name'], values=[]))
        enum.values.append(result['enum_value'])
        enums_lookup[result['enum_name']] = enum
    enums = [e for e in enums_lookup.values()]

    await conn.close()
    return tables, enums
