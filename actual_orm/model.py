from typing import (
    get_origin,
    Annotated,
    get_args,
    Optional,
    Any,
    Type,
    Generic,
    List,
    Tuple,
    TypeVar,
    Mapping,
)
import re
from asyncpg import Connection
from .query_builder.conditions import Condition, LogicalCondition, AndCondition
from .query_builder.query_builder import QueryBuilder, OrderByDirection
from .dot_dict import DotDict
from .query_builder.model_column import ModelColumn


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


T = TypeVar("T", bound="Model")


class MetaModel(type):
    def __init__(cls: Type["Model"], name, bases, dict):
        super().__init__(name, bases, dict)  # type: ignore

        cls.columns: DotDict[ModelColumn] = DotDict()
        for name in cls.__annotations__.keys():
            cls.columns[name] = ModelColumn(table=cls.__table_name__, name=name)


CreateT = TypeVar("CreateT", bound=Mapping[str, Any])
UpdateT = TypeVar("UpdateT", bound=Mapping[str, Any])


# class Model:
class Model(Generic[CreateT, UpdateT], metaclass=MetaModel):
    __table_name__: str = ""
    __indexes__ = []

    _primary_key: str | None = None
    _required_fields_to_insert: List[str] | None = None
    _updated_at_columns: List[str] | None = None

    @classmethod
    def builder(cls: Type[T]) -> QueryBuilder[T]:
        query_builder = QueryBuilder()
        query_builder.table = cls.__table_name__
        query_builder.return_as(cls)
        return query_builder

    @classmethod
    def create_test[T](cls: T, data: T):
        pass

    @classmethod
    def _get_updated_at_columns(cls):
        if cls._updated_at_columns != None:
            return cls._updated_at_columns

        columns = []
        for column_name, type in cls.__annotations__.items():
            is_annotated = get_origin(type) is Annotated
            if is_annotated == False:
                continue
            _, *annotations = get_args(type)
            if {"updated_at": True} in annotations:
                columns.append(column_name)

        cls._updated_at_columns = columns
        return cls._updated_at_columns

    @classmethod
    def _get_primary_key(cls) -> str:
        if cls._primary_key != None:
            return cls._primary_key

        for column_name, type in cls.__annotations__.items():
            is_annotated = get_origin(type) is Annotated
            if is_annotated == False:
                continue
            _, *annotations = get_args(type)
            if {"primary_key": True} in annotations:
                cls._primary_key = column_name
                break

        return cls._primary_key or ""

    @classmethod
    def _get_required_fields_to_insert(cls: Type[T]):
        if cls._required_fields_to_insert != None:
            return cls._required_fields_to_insert

        field_names = []
        for column_name, type in cls.__annotations__.items():
            is_annotated = get_origin(type) is Annotated

            if is_annotated == False:
                if get_origin(type) != Optional:
                    field_names.append(column_name)
                    continue
            else:
                data_type, *annotations = get_args(type)
                if get_origin(data_type) is Optional or any(
                    "nullable" in annotation
                    or "default" in annotation
                    or "auto_increment" in annotation
                    for annotation in annotations
                ):
                    continue
                else:
                    field_names.append(column_name)
        cls._required_fields_to_insert = field_names
        return cls._required_fields_to_insert

    @classmethod
    async def get(
        cls: Type[T],
        *conditions: LogicalCondition,
        conn: Connection | None = None,
    ) -> T | None:
        result: List[T] = (
            await QueryBuilder()
            .select(cls.__table_name__)
            .where(AndCondition(*list(conditions)))
            .limit(1)
            .return_as(cls)
            .run(conn)
        )
        if len(result) == 0:
            return None
        return result[0]

    @classmethod
    async def query(
        cls: Type[T],
        condition: LogicalCondition | None = None,
        order_by: List[Tuple["ModelColumn", OrderByDirection]] | None = None,
        limit: int | None = None,
        conn: Connection | None = None,
    ):
        query_builder = QueryBuilder().select(cls.__table_name__)

        if condition != None:
            query_builder = query_builder.where(condition)

        if order_by != None:
            query_builder = query_builder.order_by(*order_by)

        if limit != None:
            query_builder = query_builder.limit(limit)

        query_builder = query_builder.return_as(cls)

        result: List[T] = await query_builder.run(conn)
        return result

    @classmethod
    async def create(cls: Type[T], data: CreateT, conn: Connection | None = None) -> T:
        results: List[T] = (
            await QueryBuilder()
            .insert(cls.__table_name__, dict(data))
            .return_as(cls)
            .run(conn)
        )
        return results[0]

    @classmethod
    async def create_many(
        cls: Type[T], data: List[CreateT], conn: Connection | None = None
    ) -> List[T]:
        new_data = [dict(d) for d in data]
        results: List[T] = (
            await QueryBuilder()
            .insert(cls.__table_name__, new_data)
            .return_as(cls)
            .run(conn)
        )
        return results

    @classmethod
    async def update(
        cls: Type[T],
        data: UpdateT,
        condition: LogicalCondition,
        conn: Connection | None = None,
    ):
        result: List[T] = (
            await QueryBuilder()
            .update(cls.__table_name__, dict(data))
            .where(condition)
            .return_as(cls)
            .run(conn)
        )
        return result

    @classmethod
    async def upsert(
        cls: Type[T],
        where: LogicalCondition,
        create: CreateT,
        update: UpdateT,
        conn: Connection | None = None,
    ) -> T:
        existing = (
            await QueryBuilder()
            .select(cls.__table_name__)
            .where(where)
            .return_as(cls)
            .run(conn)
        )
        if len(existing) > 1:
            raise Exception("Where condition for upsert was not unique")

        if len(existing) == 1:
            if len(update.keys()) == 0:
                return existing[0]
            
            result = (
                await QueryBuilder()
                .update(cls.__table_name__, data=dict(update))
                .where(where)
                .return_as(cls)
                .run()
            )
            return result[0]
        else:
            result = (
                await QueryBuilder()
                .insert(cls.__table_name__, data=dict(create))
                .return_as(cls)
                .run()
            )
            return result[0]

    async def update_self(self: T, conn: Connection | None = None) -> T:
        primary_key_column = self.__class__._get_primary_key()
        data = {}
        for key in self.__annotations__.keys():
            if primary_key_column == key:
                continue
            data[key] = getattr(self, key)

        result: List[T] = (
            await QueryBuilder()
            .update(self.__class__.__table_name__, data)
            .where(
                self.columns[primary_key_column] == getattr(self, primary_key_column)
            )
            .return_as(self.__class__)
            .run(conn)
        )
        return result[0]

    @classmethod
    async def delete(
        cls: Type[T], *conditions: LogicalCondition, conn: Connection | None = None
    ):
        await QueryBuilder().delete(cls.__table_name__).where(
            AndCondition(*list(conditions))
        ).run()

    async def delete_self(self, conn: Connection | None = None):
        primary_key_column = self.__class__._get_primary_key()
        primary_key_value = getattr(self, primary_key_column)
        await QueryBuilder().delete(self.__class__.__table_name__).where(
            self.__class__.columns[primary_key_column] == primary_key_value
        ).run(conn)

    # @classmethod
    # async def upsert[
    #     T
    # ](
    #     cls: Type[T],
    #     model: T,
    #     unique_columns: List[str] | None = None,
    #     conn: Connection | None = None,
    # ):
    #     async with _get_connection(conn) as conn:
    #         updated_at_columns = cls._get_updated_at_columns()
    #         for column_name in updated_at_columns:
    #             setattr(
    #                 model, column_name, datetime.datetime.now(datetime.timezone.utc)
    #             )

    #         fields_to_insert = {}
    #         required_fields = cls._get_required_fields_to_insert()
    #         for property in fields(model):
    #             if (
    #                 property.name in required_fields
    #                 or getattr(model, property.name) != None
    #             ):
    #                 fields_to_insert[property.name] = getattr(model, property.name)

    #         if unique_columns == None:
    #             unique_indexes = [
    #                 index.columns
    #                 for index in cls.__indexes__
    #                 if isinstance(index, UniqueIndex)
    #                 and all(key in fields_to_insert for key in index.columns)
    #             ]
    #             unique_columns = next(
    #                 iter(unique_indexes),
    #                 [
    #                     (
    #                         cls._get_primary_key()
    #                         if cls._get_primary_key() in fields_to_insert
    #                         else None
    #                     )
    #                 ],
    #             )
    #             if unique_columns == None:
    #                 raise Exception(
    #                     "No unique columns intersect with the provided data", cls, model
    #                 )

    #         result = await conn.fetch(
    #             f"""
    #             INSERT INTO {cls.__table_name__}
    #             ({",".join([key for key in fields_to_insert.keys()])})
    #             VALUES
    #             ({",".join([f"${i}" for i in range(1, len(fields_to_insert.keys()) + 1)])})
    #             ON CONFLICT ({",".join(unique_columns)})
    #             DO UPDATE SET
    #                 {",\n".join([f"{key} = ${i+1}" for i, key in enumerate(fields_to_insert.keys())])}
    #             RETURNING {", ".join([name for name in cls.__annotations__.keys()])}
    #         """,
    #             *[value for value in fields_to_insert.values()],
    #         )

    #         return cls(**result[0])
