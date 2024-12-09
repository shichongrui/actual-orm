import os
from dotenv import dotenv_values

def find_env_file():
    current_dir = os.getcwd()
    
    while True:
        # Check if requirements.txt exists in the current directory
        if os.path.exists(os.path.join(current_dir, 'requirements.txt')):
            # Look for .env file in this directory
            env_path = os.path.join(current_dir, '.env')
            if os.path.exists(env_path):
                return env_path
            else:
                raise FileNotFoundError("No .env file found in the same directory as requirements.txt")
        
        # Move up one directory
        current_dir = os.path.dirname(current_dir)
        
        # If we reach the root directory and haven't found requirements.txt, stop
        if current_dir == os.path.abspath(os.sep):
            raise FileNotFoundError("Could not find requirements.txt in any parent directory")

env_file_path = find_env_file()
config = dotenv_values(env_file_path)

def get_database_url():
    return config["DATABASE_URL"]