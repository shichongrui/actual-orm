import os
import importlib
import asyncpg


async def run_migrations(database_url: str):
    migration_file_names = os.listdir("database/migrations")

    conn = await asyncpg.connect(database_url)
    await conn.execute(
        """CREATE TABLE IF NOT EXISTS _actual_orm_migrations (
                name TEXT,
                ran_at TIMESTAMPTZ(3) DEFAULT NOW()
            );"""
    )
    already_ran = await conn.fetch("""
        SELECT name
        FROM _actual_orm_migrations    
    """)

    for migration_file_name in sorted(migration_file_names):
        if migration_file_name.endswith(".py") == False:
            continue

        migration_name = migration_file_name.replace(".py", "")
        module = importlib.import_module(f"database.migrations.{migration_name}")

        if migration_name in [record["name"] for record in already_ran]:
            continue
        
        # TODO: Keep track of all migrations in the database so we know which ones
        # have been run and which ones have not

        migrate = getattr(module, "migrate")
        async with conn.transaction():
            await migrate(conn)
            await conn.execute("""
                INSERT INTO _actual_orm_migrations
                (name)
                VALUES
                ($1)
            """, migration_name)
