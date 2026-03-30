"""
NaviAid Auth Utilities – Password hashing, JWT creation and verification.
Uses bcrypt directly to avoid passlib/bcrypt version conflicts.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib
import secrets

import jwt

from app.config import settings


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-SHA256 (no bcrypt version issues)."""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260000)
    return f"pbkdf2$sha256$260000${salt}${hashed.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a PBKDF2-SHA256 password."""
    try:
        parts = hashed_password.split("$")
        if len(parts) != 5:
            return False
        _, algo, iterations, salt, stored_hash = parts
        hashed = hashlib.pbkdf2_hmac(
            algo, plain_password.encode(), salt.encode(), int(iterations)
        )
        return hashed.hex() == stored_hash
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
