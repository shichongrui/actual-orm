import pytest_asyncio
import asyncpg
import actual_orm.cli.utils as utils
from actual_orm import close, configure

DATABASE_URL = "postgresql://postgres:password@localhost:5432/"
DB_NAME = "actual_orm_test"

@pytest_asyncio.fixture(scope='module')
async def db():
    db_conn = await asyncpg.connect(DATABASE_URL)
    await db_conn.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
    await db_conn.execute(f"CREATE DATABASE {DB_NAME}")
    await db_conn.close()

    await utils.run_migrations(DATABASE_URL+DB_NAME)

    configure(DATABASE_URL+DB_NAME)
    yield 
    await close()