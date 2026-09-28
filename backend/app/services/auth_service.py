from datetime import datetime, timedelta, timezone
from typing import Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import ForbiddenException, UnauthorizedException
from app.models.auth import User
from app.security.jwt import create_access_token, create_refresh_token, decode_token, revoke_token
from app.security.password import verify_password
from app.services.audit_service import log_audit_event

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
    client_ip: str = "unknown",
) -> Tuple[User, str, str]:
    stmt = select(User).where(User.email == email)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    now = datetime.now(timezone.utc)

    if not user:
        # Audit failed login with unknown principal
        await log_audit_event(
            db=db,
            action="FAILED_LOGIN",
            resource_type="USER",
            resource_id=email,
            result="FAILURE",
            actor_email=email,
            metadata={"ip": client_ip, "reason": "User not found"},
        )
        raise UnauthorizedException("Invalid email or password")

    # Check lockout
    locked_until = user.locked_until
    if locked_until and locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)

    if locked_until and locked_until > now:
        remaining = int((locked_until - now).total_seconds() / 60)
        await log_audit_event(
            db=db,
            action="FAILED_LOGIN",
            resource_type="USER",
            resource_id=user.id,
            result="DENIED",
            actor_id=user.id,
            actor_email=user.email,
            metadata={"ip": client_ip, "reason": "Account locked"},
        )
        raise ForbiddenException(f"Account is locked due to security policy. Retry in {remaining + 1} minutes")

    if not user.is_active:
        raise ForbiddenException("Account is deactivated")

    # Verify password hash
    if not verify_password(password, user.password_hash):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
            user.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
            await db.commit()
            await log_audit_event(
                db=db,
                action="ACCOUNT_LOCKED",
                resource_type="USER",
                resource_id=user.id,
                result="DENIED",
                actor_id=user.id,
                actor_email=user.email,
                metadata={"ip": client_ip, "failed_attempts": user.failed_login_attempts},
            )
            raise ForbiddenException("Account locked due to 5 consecutive failed login attempts. Retry in 15 minutes")

        await db.commit()
        await log_audit_event(
            db=db,
            action="FAILED_LOGIN",
            resource_type="USER",
            resource_id=user.id,
            result="FAILURE",
            actor_id=user.id,
            actor_email=user.email,
            metadata={"ip": client_ip, "attempt": user.failed_login_attempts},
        )
        raise UnauthorizedException("Invalid email or password")

    # Successful login: reset failed counters and update last_login_at
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = now
    await db.commit()

    role_name = user.role.name if user.role else "Viewer"
    access_token = create_access_token(user.id, user.email, role_name)
    refresh_token = create_refresh_token(user.id)

    await log_audit_event(
        db=db,
        action="USER_LOGIN",
        resource_type="USER",
        resource_id=user.id,
        result="SUCCESS",
        actor_id=user.id,
        actor_email=user.email,
        metadata={"ip": client_ip, "role": role_name},
    )

    return user, access_token, refresh_token


async def refresh_user_token(
    db: AsyncSession,
    refresh_token: str,
) -> Tuple[str, str]:
    payload = decode_token(refresh_token, expected_type="refresh")
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid refresh token")

    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not user.is_active:
        raise UnauthorizedException("User inactive or no longer exists")

    # Invalidate old refresh token (token rotation)
    revoke_token(refresh_token)

    role_name = user.role.name if user.role else "Viewer"
    new_access_token = create_access_token(user.id, user.email, role_name)
    new_refresh_token = create_refresh_token(user.id)

    return new_access_token, new_refresh_token


async def logout_user(
    db: AsyncSession,
    user: User,
    token: str,
) -> None:
    revoke_token(token)
    await log_audit_event(
        db=db,
        action="USER_LOGOUT",
        resource_type="USER",
        resource_id=user.id,
        result="SUCCESS",
        actor_id=user.id,
        actor_email=user.email,
    )
