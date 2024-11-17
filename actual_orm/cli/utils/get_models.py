import importlib.metadata
import os
import sys
import importlib
from ...model import Model

# Add the FastAPI project's root directory to sys.path
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def get_models():
    model_files = os.listdir("database/models")

    models = set()
    for model_file in model_files:
        if model_file.endswith(".py") == False:
            continue

        module = importlib.import_module(
            f"database.models.{model_file.replace(".py", "")}"
        )
        for attribute_name in dir(module):
            export = getattr(module, attribute_name)
            if (
                isinstance(export, type)
                and export != Model
                and issubclass(export, Model)
            ):
                models.add(export)

    return models
