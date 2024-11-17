import asyncio
import click
from .commands.init import init_command
from .commands.migrate_dev import migrate_dev_command
from .commands.migrate_prod import migrate_prod_command
from .commands.migrate_create import migrate_create_command
from .commands.migrate_reset import migrate_reset_command

@click.group()
def main():
    pass

@main.command()
def init():
    asyncio.run(init_command())

@main.group()
def migrate():
    pass

@migrate.command()
def dev():
    asyncio.run(migrate_dev_command())

@migrate.command()
def prod():
    asyncio.run(migrate_prod_command())

@migrate.command()
def create():
    asyncio.run(migrate_create_command())

@migrate.command()
def reset():
    asyncio.run(migrate_reset_command())

if __name__ == "__main__":
    main()