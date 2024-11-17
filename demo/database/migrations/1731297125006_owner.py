
# Migration Name: owner
# Created at: 1731297125006
from asyncpg import Connection

async def migrate(conn: Connection):
    await conn.execute('CREATE TABLE owners (id SERIAL PRIMARY KEY, external_id text NOT NULL, application_id int4 NOT NULL REFERENCES applications(id), created_at timestamptz(3) NOT NULL DEFAULT NOW(), updated_at timestamptz(3) NOT NULL DEFAULT NOW())')
                   
