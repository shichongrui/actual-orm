import click
import asyncpg
from urllib.parse import urlparse, urlunparse
from ..utils.get_database_url import get_database_url
from ..utils.run_migrations import run_migrations

async def migrate_reset_command():
    confirmed = click.confirm("Are you sure you want to reset the database?", True)
    if confirmed == False:
        return

    database_url = get_database_url()
    if database_url == None:
        raise Exception("DATABASE_URL is not set in .env")
    
    parsed_url = urlparse(database_url)

    database = parsed_url.path.lstrip("/")

    connection_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            "/",
            "",
            "",
            "",
        )
    )

    conn = await asyncpg.connect(connection_url)
    await conn.execute(f'DROP DATABASE IF EXISTS "{database}"')
    await conn.execute(f'CREATE DATABASE "{database}"')
    await conn.close()

    await run_migrations(database_url)

    click.echo("Database reset")
