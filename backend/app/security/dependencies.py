from datetime import datetime, timezone
from typing import Callable, List
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ForbiddenException, UnauthorizedException
from app.database.session import get_db
from app.models.auth import User
from app.security.jwt import decode_token

security_scheme = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_token(token, expected_type="access")
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Malformed token payload: missing subject")

    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        raise UnauthorizedException("User associated with token no longer exists")

    if not user.is_active:
        raise ForbiddenException("Account is disabled. Contact your security administrator")

    # Check progressive lockout
    locked_until = user.locked_until
    if locked_until and locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)
    if locked_until and locked_until > datetime.now(timezone.utc):
        raise ForbiddenException("Account is temporarily locked due to repeated failed logins")

    return user


def require_role(*allowed_roles: str) -> Callable:
    """
    Server-side authorization dependency ensuring current user holds one of allowed roles.
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = current_user.role.name if current_user.role else ""
        if user_role not in allowed_roles:
            raise ForbiddenException(
                f"Role '{user_role}' is not authorized for this operation. Required: {list(allowed_roles)}"
            )
        return current_user

    return role_checker


def require_permission(required_permission: str) -> Callable:
    """
    Server-side authorization dependency checking specific permission grant.
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = {p.name for p in current_user.role.permissions} if current_user.role else set()
        if required_permission not in user_permissions:
            raise ForbiddenException(f"Missing required permission: '{required_permission}'")
        return current_user

    return permission_checker
