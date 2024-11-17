from typing import Any, Union, List
from dataclasses import dataclass
from .model_column import ModelColumn
from ..nanoid import nanoid

LogicalCondition = Union["Condition", "AndCondition", "OrCondition"]

@dataclass
class Condition:
    column: ModelColumn
    condition: str
    value: Any

    def to_sql(self):
        if isinstance(self.value, ModelColumn):
            return (
                f"{self.column.table}.{self.column.name} {self.condition} {self.value.table}.{self.value.name}",
                {},
            )

        parameter_name = f"condition_{self.column.table}_{self.column.name}_{nanoid()}"

        if self.condition == "in":
            return f"{self.column.table}.{self.column.name} = ANY(:{parameter_name})", {
                parameter_name: self.value
            }

        return (
            f"{self.column.table}.{self.column.name} {self.condition} :{parameter_name}",
            {parameter_name: self.value},
        )

@dataclass
class OrCondition:
    conditions: List[LogicalCondition]

    def __init__(self, *conditions: LogicalCondition):
        self.conditions = list(conditions)

    def to_sql(self):
        parameters = {}
        sql_statements = []
        for condition in self.conditions:
            condition_sql, condition_parameters = condition.to_sql()
            sql_statements.append(condition_sql)
            parameters.update(condition_parameters)
        return f"({" OR ".join(sql_statements)})", parameters


@dataclass
class AndCondition:
    conditions: List[LogicalCondition]

    def __init__(self, *conditions: LogicalCondition):
        self.conditions = list(conditions)

    def to_sql(self):
        parameters = {}
        sql_statements = []
        for condition in self.conditions:
            condition_sql, condition_parameters = condition.to_sql()
            sql_statements.append(condition_sql)
            parameters.update(condition_parameters)
        return f"({" AND ".join(sql_statements)})", parameters

