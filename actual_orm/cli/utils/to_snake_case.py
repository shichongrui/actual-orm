import re

def to_snake_case(class_name: str) -> str:
    # Use a regular expression to add underscores between lowercase and uppercase letters
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', class_name).lower()
