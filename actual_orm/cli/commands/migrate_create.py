import click
from typing import List
from time import time

async def migrate_create_command():
    ms_date_time = int(time() * 1000)
    name = click.prompt("Migration Name", type=str)
    file_name = f"database/migrations/{ms_date_time}_{name}.py"
    with open(file_name, "w") as file:
        file.write(f"""
# Migration Name: {name}
# Created at: {ms_date_time}
from asyncpg import Connection

async def migrate(conn: Connection):
    # Add migration here
    await conn.execute("")

""")
    