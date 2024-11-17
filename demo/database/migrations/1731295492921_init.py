
# Migration Name: init
# Created at: 1731295492921
from asyncpg import Connection

async def migrate(conn: Connection):
    await conn.execute('CREATE TABLE applications (id SERIAL PRIMARY KEY, external_id text NOT NULL, title text NOT NULL, created_at timestamptz(3) NOT NULL DEFAULT NOW())')
                   
