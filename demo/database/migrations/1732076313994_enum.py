
# Migration Name: enum
# Created at: 1732076313994
from asyncpg import Connection

async def migrate(conn: Connection):
    await conn.execute("CREATE TYPE content_type AS ENUM ('markdown', 'text', 'vtt', 'pdf')")
                   
