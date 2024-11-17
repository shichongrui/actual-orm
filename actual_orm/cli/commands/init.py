import os
import click

async def init_command():
    user = click.prompt("Database user", type=str, default="postgres")
    password = click.prompt("Database password", type=str, default="password")
    host = click.prompt("Database host", type=str, default="localhost")
    port = click.prompt("Database port", type=str, default="5432")
    database = click.prompt("Database name", type=str)

    if os.path.isdir("database/migrations") == False:
        os.makedirs("database/migrations")
    if os.path.isdir("database/models") == False:
        os.makedirs("database/models")

    database_url = f"postgres://{user}:{password}@{host}:{port}/{database}"
    with open(".env", "a" if os.path.isfile(".env") == True else "w") as file:
        file.write(f"\nDATABASE_URL={database_url}\n")
    