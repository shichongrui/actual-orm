import secrets
import string

# Define Nano ID–like alphabet
alphabet = string.ascii_letters

def nanoid():
    # Generate a 21-character ID
    return ''.join(secrets.choice(alphabet) for _ in range(10))