
# Migration Name: content
# Created at: 1731297312887
from asyncpg import Connection

async def migrate(conn: Connection):
    await conn.execute('CREATE TABLE content (id SERIAL PRIMARY KEY, title text NOT NULL, external_id text NOT NULL, hash varchar(64) NOT NULL, full_text text NOT NULL, context_id text NOT NULL, created_at timestamptz(3) NOT NULL DEFAULT NOW(), updated_at timestamptz(3) NOT NULL DEFAULT NOW())')
                   
