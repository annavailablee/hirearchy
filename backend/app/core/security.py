from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.config import settings

# Argon2id via pwdlib. Recommended hash for new applications.
_password_hash = PasswordHash.recommended()


def hash_password(plain: str) -> str:
    return _password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _password_hash.verify(plain, hashed)


def create_access_token(subject: str) -> str:
    """Create a signed JWT. `subject` is the user id."""
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Raises jwt.PyJWTError on invalid/expired tokens."""
    return jwt.decode(
        token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
    )