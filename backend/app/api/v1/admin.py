from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictException, NotFoundException
from app.database.session import get_db
from app.models.audit import AuditLog
from app.models.auth import Role, User
from app.models.dlp import SecurityPolicy
from app.schemas.admin import AuditLogResponse, PolicyCreateRequest, PolicyResponse, PolicyUpdateRequest
from app.schemas.auth import UserCreateRequest, UserResponse
from app.security.dependencies import require_role
from app.security.password import hash_password
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/users", response_model=List[UserResponse], dependencies=[Depends(require_role("Admin"))])
async def list_users(
    db: AsyncSession = Depends(get_db),
):
    """
    List all platform users with account status and strike metrics. Admin only.
    """
    stmt = select(User).order_by(User.created_at.desc())
    res = await db.execute(stmt)
    users = res.scalars().all()

    return [
        UserResponse(
            id=u.id,
            email=u.email,
            name=u.name,
            role=u.role.name if u.role else "Viewer",
            is_active=u.is_active,
            created_at=u.created_at,
            permissions=[p.name for p in u.role.permissions] if u.role else [],
            failed_login_attempts=u.failed_login_attempts,
            last_login_at=u.last_login_at,
        )
        for u in users
    ]


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("Admin"))],
)
async def create_user(
    payload: UserCreateRequest,
    current_admin: User = Depends(require_role("Admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Provision a new user account with deterministic RBAC role. Admin only.
    """
    # 1. Check for duplicate email
    stmt = select(User).where(User.email == payload.email)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise ConflictException(f"User with email '{payload.email}' already exists")

    # 2. Resolve Role
    role_stmt = select(Role)
    role_res = await db.execute(role_stmt)
    all_roles = role_res.scalars().all()
    target_role = next(
        (r for r in all_roles if r.name.upper() == payload.role_name.strip().upper()),
        None,
    )
    if not target_role:
        target_role = next((r for r in all_roles if r.name == "Viewer"), all_roles[0] if all_roles else None)

    if not target_role:
        raise NotFoundException("Role", payload.role_name)

    # 3. Create User with hashed password
    new_user = User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
        role_id=target_role.id,
        is_active=True,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # 4. Audit Log
    await log_audit_event(
        db=db,
        action="USER_PROVISIONED",
        resource_type="USER",
        resource_id=new_user.id,
        result="SUCCESS",
        actor_id=current_admin.id,
        actor_email=current_admin.email,
        metadata={"email": new_user.email, "role": target_role.name},
    )

    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        role=target_role.name,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        permissions=[p.name for p in target_role.permissions] if target_role.permissions else [],
        failed_login_attempts=0,
        last_login_at=None,
    )


@router.get(
    "/policies",
    response_model=List[PolicyResponse],
    dependencies=[Depends(require_role("Admin", "Analyst", "Viewer"))],
)
async def list_security_policies(
    policy_type: Optional[str] = Query(None, description="DLP, RATE_LIMIT, ACCESS_CONTROL"),
    db: AsyncSession = Depends(get_db),
):
    """
    List security and DLP policies.
    """
    stmt = select(SecurityPolicy)
    if policy_type:
        stmt = stmt.where(SecurityPolicy.policy_type == policy_type.upper())
    stmt = stmt.order_by(SecurityPolicy.created_at.desc())
    res = await db.execute(stmt)
    policies = res.scalars().all()

    return [
        PolicyResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            policy_type=p.policy_type,
            configuration=p.configuration,
            enabled=p.enabled,
        )
        for p in policies
    ]


@router.post(
    "/policies",
    response_model=PolicyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("Admin"))],
)
async def create_security_policy(
    payload: PolicyCreateRequest,
    current_admin: User = Depends(require_role("Admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new security or DLP policy. Gated strictly to Administrator role.
    """
    policy = SecurityPolicy(
        name=payload.name,
        description=payload.description,
        policy_type=payload.policy_type,
        configuration=payload.configuration,
        enabled=payload.enabled,
        created_by=current_admin.id,
    )
    db.add(policy)
    await db.commit()
    await db.refresh(policy)

    # Log immutable audit event
    await log_audit_event(
        db=db,
        action="POLICY_CREATED",
        resource_type="SECURITY_POLICY",
        resource_id=policy.id,
        result="SUCCESS",
        actor_id=current_admin.id,
        actor_email=current_admin.email,
        metadata={"name": policy.name, "type": policy.policy_type},
    )

    return PolicyResponse(
        id=policy.id,
        name=policy.name,
        description=policy.description,
        policy_type=policy.policy_type,
        configuration=policy.configuration,
        enabled=policy.enabled,
    )


@router.put(
    "/policies/{policy_id}",
    response_model=PolicyResponse,
    dependencies=[Depends(require_role("Admin"))],
)
async def update_security_policy(
    policy_id: str,
    payload: PolicyUpdateRequest,
    current_admin: User = Depends(require_role("Admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    Update or toggle security policy state. Admin only.
    """
    stmt = select(SecurityPolicy).where(SecurityPolicy.id == policy_id)
    res = await db.execute(stmt)
    policy = res.scalar_one_or_none()

    if not policy:
        raise NotFoundException("SecurityPolicy", policy_id)

    if payload.enabled is not None:
        policy.enabled = payload.enabled
    if payload.configuration is not None:
        policy.configuration = payload.configuration
    if payload.description is not None:
        policy.description = payload.description

    await db.commit()
    await db.refresh(policy)

    await log_audit_event(
        db=db,
        action="POLICY_UPDATED",
        resource_type="SECURITY_POLICY",
        resource_id=policy.id,
        result="SUCCESS",
        actor_id=current_admin.id,
        actor_email=current_admin.email,
        metadata={"name": policy.name, "enabled": policy.enabled},
    )

    return PolicyResponse(
        id=policy.id,
        name=policy.name,
        description=policy.description,
        policy_type=policy.policy_type,
        configuration=policy.configuration,
        enabled=policy.enabled,
    )


@router.get(
    "/audit-logs",
    response_model=List[AuditLogResponse],
    dependencies=[Depends(require_role("Admin", "Analyst"))],
)
async def get_audit_logs(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve system audit log trail. Allowed for Admin and Analyst roles.
    """
    stmt = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit)
    res = await db.execute(stmt)
    logs = res.scalars().all()

    return [
        AuditLogResponse(
            id=log.id,
            actor_email=log.actor_email,
            action=log.action,
            resource_type=log.resource_type,
            resource_id=log.resource_id,
            result=log.result,
            metadata=log.metadata_payload,
            timestamp=log.timestamp.isoformat(),
        )
        for log in logs
    ]
