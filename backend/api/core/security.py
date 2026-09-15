from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from api.core.env import env


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return password_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return password_context.verify(plain, hashed)


def create_access_token(subject: int | str, extra: dict[str, Any] | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=env.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    payload: dict[str, Any] = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    
    if extra:
        payload.update(extra)

    return jwt.encode(payload, env.SECRET_KEY, algorithm="HS256")

def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, env.SECRET_KEY, algorithms=["HS256"])
