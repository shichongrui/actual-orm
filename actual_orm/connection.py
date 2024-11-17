from typing import AsyncGenerator
import asyncio
import asyncpg
from contextlib import asynccontextmanager
from weakref import WeakKeyDictionary

# Use WeakKeyDictionary to automatically clean up closed event loops
connection_url: str | None = None
connection_pools = WeakKeyDictionary()

def configure(database_url: str):
    global connection_url
    connection_url = database_url

async def get_or_create_pool() -> asyncpg.Pool:
    global connection_url, connection_pools
    loop = asyncio.get_running_loop()

    # Retrieve or create the pool for the current event loop
    if loop not in connection_pools:
        if not connection_url:
            raise ValueError("Database URL is not configured. Call 'configure()' with a valid URL.")
        
        # Initialize and store a new pool for this event loop
        connection_pools[loop] = await asyncpg.create_pool(connection_url)
    
    return connection_pools[loop]

@asynccontextmanager
async def get_connection(conn: asyncpg.Connection | None = None) -> AsyncGenerator[asyncpg.Connection, None]:
    pool = await get_or_create_pool()
    if conn is None:
        async with pool.acquire() as connection:
            yield connection
    else:
        yield conn

@asynccontextmanager
async def start_transaction(conn: asyncpg.Connection | None = None):
    async with get_connection(conn) as conn:
        async with conn.transaction():
            yield conn

async def close():
    # Close all connection pools and clear the WeakKeyDictionary
    pool = await get_or_create_pool()
    await pool.close()

