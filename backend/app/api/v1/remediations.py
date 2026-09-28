from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictException, NotFoundException
from app.database.session import get_db
from app.models.auth import User
from app.models.incident import RemediationAction
from app.schemas.remediation import (
    RemediationActionResponse,
    RemediationApprovalRequest,
    RemediationRejectionRequest,
)
from app.security.dependencies import get_current_user, require_role
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/remediations", tags=["Human-in-the-Loop Remediation"])


@router.get("", response_model=List[RemediationActionResponse], dependencies=[Depends(get_current_user)])
async def list_remediations(
    status_filter: Optional[str] = Query(None, alias="status"),
    incident_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    List remediation actions. Filterable by status (e.g. PENDING_APPROVAL) and incident.
    """
    query = select(RemediationAction).order_by(RemediationAction.created_at.desc())
    if status_filter:
        query = query.where(RemediationAction.status == status_filter.upper())
    if incident_id:
        query = query.where(RemediationAction.incident_id == incident_id)

    query = query.offset(offset).limit(limit)
    res = await db.execute(query)
    actions = res.scalars().all()
    return actions


@router.post(
    "/{action_id}/approve",
    response_model=RemediationActionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role("Admin"))],
)
async def approve_remediation_action(
    action_id: str,
    payload: RemediationApprovalRequest,
    current_admin: User = Depends(require_role("Admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    HUMAN-IN-THE-LOOP APPROVAL GATE:
    Strictly restricted to Admin role.
    Approves and executes the simulated high-risk remediation action.
    """
    stmt = select(RemediationAction).where(RemediationAction.id == action_id)
    res = await db.execute(stmt)
    action = res.scalar_one_or_none()

    if not action:
        raise NotFoundException("RemediationAction", action_id)

    if action.status != "PENDING_APPROVAL":
        raise ConflictException(f"Action cannot be approved because current status is '{action.status}'")

    now = datetime.now(timezone.utc)
    action.status = "EXECUTED"
    action.approved_by = current_admin.id
    action.executed_at = now
    action.execution_result = {
        "status": "SUCCESS",
        "mode": "SIMULATED_SAFE_EXECUTION",
        "action_type": action.action_type,
        "notes": payload.notes or "Approved by security administrator",
        "execution_timestamp": now.isoformat(),
    }

    await db.commit()
    await db.refresh(action)

    await log_audit_event(
        db=db,
        action="REMEDIATION_APPROVED",
        resource_type="REMEDIATION_ACTION",
        resource_id=action.id,
        result="SUCCESS",
        actor_id=current_admin.id,
        actor_email=current_admin.email,
        metadata={
            "action_type": action.action_type,
            "incident_id": action.incident_id,
            "notes": payload.notes,
        },
    )

    return action


@router.post(
    "/{action_id}/reject",
    response_model=RemediationActionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role("Admin"))],
)
async def reject_remediation_action(
    action_id: str,
    payload: RemediationRejectionRequest,
    current_admin: User = Depends(require_role("Admin")),
    db: AsyncSession = Depends(get_db),
):
    """
    HUMAN-IN-THE-LOOP REJECTION GATE:
    Admin rejects remediation action with mandatory recorded reason.
    """
    stmt = select(RemediationAction).where(RemediationAction.id == action_id)
    res = await db.execute(stmt)
    action = res.scalar_one_or_none()

    if not action:
        raise NotFoundException("RemediationAction", action_id)

    if action.status != "PENDING_APPROVAL":
        raise ConflictException(f"Action cannot be rejected because current status is '{action.status}'")

    action.status = "REJECTED"
    action.approved_by = current_admin.id
    action.rejection_reason = payload.reason

    await db.commit()
    await db.refresh(action)

    await log_audit_event(
        db=db,
        action="REMEDIATION_REJECTED",
        resource_type="REMEDIATION_ACTION",
        resource_id=action.id,
        result="SUCCESS",
        actor_id=current_admin.id,
        actor_email=current_admin.email,
        metadata={
            "action_type": action.action_type,
            "incident_id": action.incident_id,
            "reason": payload.reason,
        },
    )

    return action
