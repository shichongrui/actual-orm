
# Migration Name: defaults
# Created at: 1731296268797
from asyncpg import Connection

async def migrate(conn: Connection):
    await conn.execute('ALTER TABLE api_keys ALTER COLUMN updated_at SET DEFAULT NOW()')
    await conn.execute('ALTER TABLE applications ALTER COLUMN updated_at SET DEFAULT NOW()')
                   
