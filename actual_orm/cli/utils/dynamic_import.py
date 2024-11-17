import os
import importlib

def dynamic_import(file_path):
    # Get the absolute path of the file
    file_path = os.path.abspath(file_path)

    # Create a module name from the file name (without extension)
    module_name = os.path.splitext(os.path.basename(file_path))[0]

    # Load the module dynamically
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module