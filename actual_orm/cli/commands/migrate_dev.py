import click
from ..utils.get_database_url import get_database_url
from ..utils.get_models import get_models
from ..utils.model_schema import get_models_schema
from ..utils.database_schema import get_database_schema
from ..utils.schema_differ import get_schema_diff_actions
from ..utils.action import action_to_sql
from ..utils.write_migration import write_migration
from ..utils.run_migrations import run_migrations

async def migrate_dev_command():
    database_url = get_database_url()

    if database_url == None:
        raise Exception("DATABASE_URL is not defined in .env")

    await run_migrations(database_url)

    database_schema = await get_database_schema(database_url)
    model_schema = get_models_schema()

    actions = get_schema_diff_actions(model_schema=model_schema, database_schema=database_schema)

    if len(actions) == 0:
        click.echo("Database is up to date with schema")
        return

    actions_sql = [action_to_sql(action) for action in actions]

    print("Pending migration:")
    for sql in actions_sql:
        print(sql)

    write_migration([sql for sql in actions_sql if sql != None])
    await run_migrations(database_url)