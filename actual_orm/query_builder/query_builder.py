from typing import List, Optional, Tuple, Dict, TypeVar, Type, Generic
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import StrEnum, auto
from asyncpg import Connection
import re
from .. import get_connection
from .model_column import ModelColumn
from .conditions import LogicalCondition, Condition
from ..nanoid import nanoid

def convert_named_to_positional(sql: str, params: dict):
    # Find all named parameters
    param_names = re.findall(r":(\w+)", sql)
    # Replace named parameters with positional ones like $1, $2, ...
    transformed_sql = sql
    for i, name in enumerate(param_names):
        transformed_sql = transformed_sql.replace(f":{name}", f"${i+1}")
    # Reorder the parameters according to their position in the query
    transformed_params = [params[name] for name in param_names]
    return transformed_sql, transformed_params

class OrderByDirection(StrEnum):
    ASC = auto()
    DESC = auto()


class QueryType(StrEnum):
    SELECT = auto()
    INSERT = auto()
    UPDATE = auto()
    DELETE = auto()

@dataclass
class Join:
    type: str
    table: str
    condition: LogicalCondition

    def to_sql(self):
        condition_sql, parameters = self.condition.to_sql()
        return f"{self.type} {self.table} ON {condition_sql}", parameters

T = TypeVar('T')

class QueryBuilder(Generic[T]):
    query_type: QueryType | None
    table: str | None
    is_distinct: bool
    joins: List[Join]
    conditions: List[LogicalCondition]
    limit_value: Optional[int]
    order_by_conditions: List[Tuple[ModelColumn, OrderByDirection] | str]
    return_columns: List[str]
    return_as_cls: Type[T] | None
    data: List[Dict] | Dict | None

    def __init__(self):
        self.return_model = None
        self.query_type = None
        self.table = None
        self.is_distinct = False
        self.joins = []
        self.conditions = []
        self.limit_value = None
        self.order_by_conditions = []
        self.return_columns = []
        self.return_as_cls = None
        self.data = None

    def select(self, table: str | None = None, columns: List[str] | None = None):
        self.query_type = QueryType.SELECT
        self.table = table or self.table
        self.return_columns = columns or self.return_columns or []

        return self

    def insert(self, table: str, data: List[Dict] | Dict):
        self.query_type = QueryType.INSERT
        self.table = table
        self.data = data
        return self

    def update(self, table: str, data: List[Dict] | Dict):
        self.query_type = QueryType.UPDATE
        self.table = table
        self.data = data
        return self

    def delete(self, table: str):
        self.query_type = QueryType.DELETE
        self.table = table
        return self
    
    def distinct(self):
        self.is_distinct = True
        return self

    def where(self, condition: LogicalCondition):
        self.conditions.append(condition)
        return self

    def join(
        self, table: str, condition: LogicalCondition, type: str = "JOIN"
    ):
        self.joins.append(Join(type, table, condition))
        return self

    def left_join(self, table: str, condition: LogicalCondition):
        self.join(table, condition, "LEFT JOIN")
        return self

    def right_join(self, table: str, condition: LogicalCondition):
        self.join(table, condition, "RIGHT JOIN")
        return self

    def inner_join(self, table: str, condition: LogicalCondition):
        self.join(table, condition, "INNER JOIN")
        return self

    def outer_join(self, table: str, condition: LogicalCondition):
        self.join(table, condition, "OUTER JOIN")
        return self

    def limit(self, limit: int):
        self.limit_value = limit
        return self

    def order_by(self, *columns: Tuple["ModelColumn", OrderByDirection] | str):
        self.order_by_conditions += columns
        return self
    
    def return_as(self, model_cls: Type[T]):
        self.return_as_cls = model_cls
        self.return_columns = list(model_cls.__annotations__.keys())
        return self

    def select_sql(self):
        if len(self.return_columns) == 0:
            raise Exception("No columns selected to return")

        parameters = {}
        query = f"SELECT "
        query += "DISTINCT " if self.is_distinct else ""
        query += ", ".join([f"{self.table}.{column}" for column in self.return_columns])
        query += f" FROM {self.table}"

        if len(self.joins) > 0:
            query += " "
            join_sql = []
            for join in self.joins:
                sql, join_params = join.to_sql()
                join_sql.append(sql)
                parameters.update(join_params)
            query += " ".join(join_sql)

        if len(self.conditions) > 0:
            query += " WHERE "
            where_sql = []
            for where_condition in self.conditions:
                sql, params = where_condition.to_sql()
                where_sql.append(sql)
                parameters.update(params)
            query += " AND ".join(where_sql)
        if self.limit_value != None:
            limit_param_name = f"limit_{nanoid()}"
            query += f" LIMIT :{limit_param_name}"
            parameters[limit_param_name] = self.limit_value
        if len(self.order_by_conditions) > 0:
            query += " ORDER BY "
            order_by = []
            for o in self.order_by_conditions:
                if isinstance(o, str):
                    order_by.append(o)
                else:
                    column, direction = o
                    order_by.append(f"{column.table}.{column.name} {direction}")
            query += ", ".join(order_by)

        return convert_named_to_positional(query, parameters)

    def insert_sql(self):
        if self.table == None:
            raise Exception("No table was selected to insert into")
        if self.data == None:
            raise Exception("No data provided to insert")
        
        query: str = "INSERT INTO "
        query += self.table
        
        columns = self.data[0].keys() if isinstance(self.data, list) else self.data.keys()
        query += f" ({", ".join(columns)})"
        
        parameters = {}
        rows_sql = []
        if isinstance(self.data, list):
            for row in self.data:
                row_sql = []
                for i, column in enumerate(columns):
                    parameter_name = f"row_{i}_{column}_{nanoid()}"
                    parameters[parameter_name] = row[column]
                    row_sql.append(f":{parameter_name}")
                rows_sql.append(f"({", ".join(row_sql)})")
        else:
            row_sql = []
            for column in columns:
                parameter_name = f"row_{column}_{nanoid()}"
                parameters[parameter_name] = self.data[column]
                row_sql.append(f":{parameter_name}")
            rows_sql.append(f"({", ".join(row_sql)})")

        query += " VALUES "
        query += ", ".join(rows_sql)


        if self.return_as_cls != None:
            query += f" RETURNING {", ".join([name for name in self.return_as_cls.__annotations__.keys()])}"

        return convert_named_to_positional(query, parameters)

    def update_sql(self):
        if self.data is None:
            raise Exception("Update data can not be None")
        if isinstance(self.data, list):
            raise Exception("Update statement can't have a list of data")

        query = f"UPDATE {self.table}"
        query += " SET "
        
        parameters = {}
        update_sql = []
        for key, value in self.data.items():
            parameter_name = f"column_{self.table}_{key}_{nanoid()}"
            update_sql.append(f"{key} = :{parameter_name}")
            parameters[parameter_name] = value
        query += ", ".join(update_sql)

        query += " WHERE "

        

        conditions_sql = []
        for condition in self.conditions:
            condition_sql, condition_parameters = condition.to_sql()
            parameters.update(condition_parameters)
            conditions_sql.append(condition_sql)

        query += " AND ".join(conditions_sql)

        if self.return_as_cls != None:
            query += f" RETURNING {", ".join([name for name in self.return_as_cls.__annotations__.keys()])}"
        
        return convert_named_to_positional(query, parameters)

    def delete_sql(self):
        query = f"DELETE FROM {self.table}"
        query += " WHERE "

        parameters = {}
        conditions_sql = []
        for condition in self.conditions:
            sql, params = condition.to_sql()
            conditions_sql.append(sql)
            parameters.update(params)

        query += " AND ".join(conditions_sql)

        return convert_named_to_positional(query, parameters)

    def sql(self):
        match self.query_type:
            case QueryType.SELECT:
                return self.select_sql()
            case QueryType.INSERT:
                return self.insert_sql()
            case QueryType.UPDATE:
                return self.update_sql()
            case QueryType.DELETE:
                return self.delete_sql()
            case _:
                raise Exception(f"Query type {self.query_type} is not implemented")

    async def run(self, conn: Connection | None = None) -> List[T]:
        async with get_connection(conn) as conn:
            sql, params = self.sql()
            results = await conn.fetch(sql, *params)
        if self.return_as_cls == None:
            return results
        else:
            return [self.return_as_cls(**result) for result in results]

