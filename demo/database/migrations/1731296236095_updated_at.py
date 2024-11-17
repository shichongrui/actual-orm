
# Migration Name: updated_at
# Created at: 1731296236095
from asyncpg import Connection

async def migrate(conn: Connection):
    await conn.execute('ALTER TABLE applications ADD COLUMN updated_at timestamptz(3) NOT NULL')
    await conn.execute('ALTER TABLE api_keys ADD COLUMN updated_at timestamptz(3) NOT NULL')
                   
