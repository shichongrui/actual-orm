from ..utils.get_database_url import get_database_url
from ..utils.run_migrations import run_migrations

async def migrate_prod_command():
    database_url = get_database_url()

    await run_migrations(database_url)