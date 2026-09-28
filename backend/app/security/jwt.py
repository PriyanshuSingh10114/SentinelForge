import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Set
import jwt
from app.core.config import settings
from app.core.errors import UnauthorizedException


# In-memory revocation set (acts as fallback / test revocation store)
REVOKED_TOKENS: Set[str] = set()


def create_token(
    data: Dict[str, Any],
    expires_delta: timedelta,
    token_type: str = "access",
) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    to_encode.update({
        "jti": str(uuid.uuid4()),
        "exp": int(expire.timestamp()),
        "iat": int(now.timestamp()),
        "type": token_type,
    })
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str, email: str, role: str) -> str:
    delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(
        data={"sub": user_id, "email": email, "role": role},
        expires_delta=delta,
        token_type="access",
    )


def create_refresh_token(user_id: str) -> str:
    delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(
        data={"sub": user_id},
        expires_delta=delta,
        token_type="refresh",
    )


def decode_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    if token in REVOKED_TOKENS:
        raise UnauthorizedException("Token has been revoked")

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "sub", "type"]},
        )
        if payload.get("type") != expected_type:
            raise UnauthorizedException(f"Invalid token type: expected {expected_type}")
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException("Token signature has expired")
    except jwt.InvalidTokenError:
        raise UnauthorizedException("Invalid token signature or malformed token")


def revoke_token(token: str) -> None:
    REVOKED_TOKENS.add(token)
