import os
import click

def find_requirements_txt(start_dir):
    """Walks up the directory tree starting from start_dir to find requirements.txt."""
    current_dir = start_dir
    while True:
        if "requirements.txt" in os.listdir(current_dir):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # This happens when we reach the root directory
            raise FileNotFoundError("No requirements.txt found")
        current_dir = parent_dir

def write_env_file(directory, database_url):
    """Writes the .env file with DATABASE_URL in the specified directory."""
    env_path = os.path.join(directory, ".env")
    with open(env_path, "a" if os.path.isfile(env_path) else "w") as file:
        file.write(f"\nDATABASE_URL={database_url}\n")

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
    write_env_file(os.getcwd(), database_url)
    