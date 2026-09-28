from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.auth import User
from app.models.incident import InvestigationReport
from app.schemas.investigation import InvestigationResponse
from app.schemas.remediation import RemediationActionResponse
from app.security.dependencies import get_current_user, require_role
from app.services.investigation_service import run_incident_investigation

router = APIRouter(prefix="/investigations", tags=["AI Security Investigations"])


@router.post(
    "/{incident_id}",
    response_model=InvestigationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("Admin", "Analyst"))],
)
async def trigger_ai_investigation(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers the LangGraph AI Security Investigator state machine for an incident.
    Collects evidence, synthesizes attack chain, generates findings, and stages
    recommended remediation actions in PENDING_APPROVAL status.
    """
    report, actions = await run_incident_investigation(
        db=db,
        incident_id=incident_id,
        analyst_user_id=current_user.id,
        analyst_email=current_user.email,
        analyst_role=current_user.role.name if current_user.role else "Analyst",
    )

    action_responses = [
        RemediationActionResponse(
            id=a.id,
            incident_id=a.incident_id,
            action_type=a.action_type,
            description=a.description,
            status=a.status,
            requested_by=a.requested_by,
            approved_by=a.approved_by,
            rejection_reason=a.rejection_reason,
            execution_result=a.execution_result,
            executed_at=a.executed_at,
            created_at=a.created_at,
        )
        for a in actions
    ]

    return InvestigationResponse(
        id=report.id,
        incident_id=report.incident_id,
        summary=report.summary,
        attack_chain=report.attack_chain or [],
        evidence=report.evidence or [],
        findings=report.findings or [],
        recommendations=report.recommendations or [],
        confidence=float(report.confidence),
        model_used=report.model_used,
        created_at=report.created_at,
        pending_remediations=action_responses,
    )


@router.get(
    "/incident/{incident_id}",
    response_model=List[InvestigationResponse],
    dependencies=[Depends(get_current_user)],
)
async def get_incident_investigations(
    incident_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all investigation reports associated with an incident.
    """
    stmt = (
        select(InvestigationReport)
        .where(InvestigationReport.incident_id == incident_id)
        .order_by(InvestigationReport.created_at.desc())
    )
    res = await db.execute(stmt)
    reports = res.scalars().all()

    return [
        InvestigationResponse(
            id=r.id,
            incident_id=r.incident_id,
            summary=r.summary,
            attack_chain=r.attack_chain or [],
            evidence=r.evidence or [],
            findings=r.findings or [],
            recommendations=r.recommendations or [],
            confidence=float(r.confidence),
            model_used=r.model_used,
            created_at=r.created_at,
            pending_remediations=[],
        )
        for r in reports
    ]
