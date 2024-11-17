from dotenv import dotenv_values

config = dotenv_values(".env")

def get_database_url():
    return config["DATABASE_URL"]