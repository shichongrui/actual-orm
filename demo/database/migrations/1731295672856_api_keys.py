
# Migration Name: api_keys
# Created at: 1731295672856
from asyncpg import Connection

async def migrate(conn: Connection):
    await conn.execute('CREATE TABLE api_keys (id SERIAL PRIMARY KEY, key uuid NOT NULL UNIQUE, active bool NOT NULL, application_id int4 NOT NULL REFERENCES applications(id), created_at timestamptz(3) NOT NULL DEFAULT NOW())')
    await conn.execute('CREATE INDEX idx_key_created_at ON api_keys (key,created_at)')
    await conn.execute('CREATE UNIQUE INDEX idx_created_at_key ON api_keys (created_at,key)')
                   
