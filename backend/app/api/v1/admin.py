from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.audit import AuditLog
from app.models.auth import User
from app.models.dlp import SecurityPolicy
from app.schemas.admin import AuditLogResponse, PolicyCreateRequest, PolicyResponse
from app.schemas.auth import UserResponse
from app.security.dependencies import require_role
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/users", response_model=List[UserResponse], dependencies=[Depends(require_role("Admin"))])
async def list_users(
    db: AsyncSession = Depends(get_db),
):
    """
    List all platform users. Admin only.
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
        )
        for u in users
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
    await db.flush()

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
