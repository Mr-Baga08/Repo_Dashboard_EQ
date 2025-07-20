from cryptography.fernet import Fernet
from app.core.config import settings

# Ensure the secret key is in the correct format (URL-safe base64-encoded 32-byte key)
# For simplicity, we'll use a key derived from the settings, but in production,
# ensure the SECRET_KEY is generated from Fernet.generate_key()
from base64 import urlsafe_b64encode
import hashlib

# Derive a 32-byte key from the SECRET_KEY
key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
fernet = Fernet(urlsafe_b64encode(key))

def encrypt(data: str) -> bytes:
    """Encrypts a string and returns bytes."""
    return fernet.encrypt(data.encode())

def decrypt(encrypted_data: bytes) -> str:
    """Decrypts bytes and returns a string."""
    return fernet.decrypt(encrypted_data).decode()
