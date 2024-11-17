
# Migration Name: add_unique_index
# Created at: 1731529649418
from asyncpg import Connection

async def migrate(conn: Connection):
    await conn.execute('CREATE UNIQUE INDEX idx_application_id_external_id ON owners (application_id,external_id)')
                   
