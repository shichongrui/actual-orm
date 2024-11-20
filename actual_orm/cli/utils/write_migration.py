import click
from typing import List
from time import time

def write_migration(sql: List[str]):
    ms_date_time = int(time() * 1000)
    name = click.prompt("Migration Name", type=str)
    file_name = f"database/migrations/{ms_date_time}_{name}.py"
    with open(file_name, "w") as file:
        file.write(f"""
# Migration Name: {name}
# Created at: {ms_date_time}
from asyncpg import Connection

async def migrate(conn: Connection):
    {'\n    '.join([f"await conn.execute(\"{statement}\")" for statement in sql])}
                   
""")