
# Migration Name: content_type
# Created at: 1732076705886
from asyncpg import Connection

async def migrate(conn: Connection):
    await conn.execute("ALTER TABLE content ADD COLUMN type content_type NOT NULL")
                   
