from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.session import get_db
from app.models.auth import User
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from app.security.dependencies import get_current_user, security_scheme
from app.services.auth_service import (
    authenticate_user,
    logout_user,
    refresh_user_token,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user with email and password.
    Returns short-lived JWT access token and refresh token.
    Applies progressive throttling on repeated failures.
    """
    client_ip = request.client.host if request.client else "unknown"
    user, access_token, refresh_token = await authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password,
        client_ip=client_ip,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Exchanges a valid refresh token for a new access token and rotated refresh token.
    """
    new_access, new_refresh = await refresh_user_token(
        db=db,
        refresh_token=payload.refresh_token,
    )
    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="Bearer",
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_user),
    credentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Revokes the current access token and logs audit event.
    """
    await logout_user(db=db, user=current_user, token=credentials.credentials)
    return {"message": "Successfully logged out and session revoked"}


@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Returns the authenticated user's profile and granted role permissions.
    """
    permissions = [p.name for p in current_user.role.permissions] if current_user.role else []
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.name if current_user.role else "Viewer",
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        permissions=permissions,
    )
