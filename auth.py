# utils/auth.py
import bcrypt

def hash_password(password: str) -> bytes:
    """Return bcrypt hashed password (bytes)."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password(password: str, hashed: bytes) -> bool:
    """Verify plaintext password against stored bcrypt hash (bytes)."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)
