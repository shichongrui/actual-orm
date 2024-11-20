
# Migration Name: init
# Created at: 1732076267268
from asyncpg import Connection

async def migrate(conn: Connection):
    await conn.execute("CREATE TABLE applications (id SERIAL PRIMARY KEY, external_id text NOT NULL, title text NOT NULL, created_at timestamptz(3) NOT NULL DEFAULT NOW(), updated_at timestamptz(3) NOT NULL DEFAULT NOW())")
    await conn.execute("CREATE TABLE api_keys (id SERIAL PRIMARY KEY, key uuid NOT NULL UNIQUE, active bool NOT NULL, application_id int4 NOT NULL REFERENCES applications(id), created_at timestamptz(3) NOT NULL DEFAULT NOW(), updated_at timestamptz(3) NOT NULL DEFAULT NOW())")
    await conn.execute("CREATE INDEX idx_api_keys_index_key_created_at ON api_keys (key,created_at)")
    await conn.execute("CREATE TABLE owners (id SERIAL PRIMARY KEY, external_id text NOT NULL, application_id int4 NOT NULL REFERENCES applications(id), created_at timestamptz(3) NOT NULL DEFAULT NOW(), updated_at timestamptz(3) NOT NULL DEFAULT NOW())")
    await conn.execute("CREATE UNIQUE INDEX idx_owners_unique_application_id_external_id ON owners (application_id,external_id)")
    await conn.execute("CREATE UNIQUE INDEX idx_api_keys_unique_created_at_key ON api_keys (created_at,key)")
    await conn.execute("CREATE TABLE content (id SERIAL PRIMARY KEY, title text NOT NULL, external_id text NOT NULL, hash varchar(64) NOT NULL, full_text text NOT NULL, context_id text NOT NULL, created_at timestamptz(3) NOT NULL DEFAULT NOW(), updated_at timestamptz(3) NOT NULL DEFAULT NOW())")
    await conn.execute("CREATE TABLE content_owners (id SERIAL PRIMARY KEY, owner_id int4 NOT NULL REFERENCES owners(id), content_id int4 NOT NULL REFERENCES content(id))")
    await conn.execute("CREATE UNIQUE INDEX idx_content_owners_unique_content_id_owner_id ON content_owners (content_id,owner_id)")
                   
