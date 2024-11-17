
# Migration Name: content_owner
# Created at: 1731297537400
from asyncpg import Connection

async def migrate(conn: Connection):
    await conn.execute('CREATE TABLE content_owners (id SERIAL PRIMARY KEY, owner_id int4 NOT NULL REFERENCES owners(id), content_id int4 NOT NULL REFERENCES content(id))')
    await conn.execute('CREATE UNIQUE INDEX idx_content_id_owner_id ON content_owners (content_id,owner_id)')
    await conn.execute('ALTER TABLE content ALTER COLUMN hash TYPE varchar(64)')
                   
