from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import NotFoundException
from app.correlation.engine import (
    build_attack_graph,
    build_timeline,
    correlate_events_into_incident,
)
from app.database.session import get_db
from app.models.auth import User
from app.models.event import SecurityEvent
from app.models.incident import Incident
from app.schemas.incident import (
    AttackGraphResponse,
    IncidentDetailResponse,
    IncidentResponse,
    IncidentStatusUpdateRequest,
)
from app.security.dependencies import get_current_user
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/incidents", tags=["Incidents & Correlation"])


@router.get("", response_model=List[IncidentResponse])
async def list_incidents(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List correlated security incidents.
    """
    query = select(Incident).order_by(Incident.detected_at.desc())
    if status_filter:
        query = query.where(Incident.status == status_filter.upper())
    if severity:
        query = query.where(Incident.severity == severity.upper())

    query = query.offset(offset).limit(limit)
    res = await db.execute(query)
    incidents = res.scalars().all()
    return incidents


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
async def get_incident_detail(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve comprehensive incident details including explainable risk factors and chronological timeline.
    """
    stmt = (
        select(Incident)
        .options(selectinload(Incident.events))
        .where(Incident.id == incident_id)
    )
    res = await db.execute(stmt)
    incident = res.scalar_one_or_none()

    if not incident:
        # Also allow querying by human-readable incident_number (e.g. INC-1042)
        stmt_num = (
            select(Incident)
            .options(selectinload(Incident.events))
            .where(Incident.incident_number == incident_id)
        )
        res_num = await db.execute(stmt_num)
        incident = res_num.scalar_one_or_none()

    if not incident:
        raise NotFoundException("Incident", incident_id)

    timeline = build_timeline(incident)
    affected_users = list(set(e.actor for e in incident.events))
    affected_assets = list(
        set(
            (e.raw_payload or {}).get("resource")
            for e in incident.events
            if (e.raw_payload or {}).get("resource")
        )
    )

    return IncidentDetailResponse(
        id=incident.id,
        incident_number=incident.incident_number,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status=incident.status,
        risk_score=incident.risk_score,
        risk_factors=incident.risk_factors or [],
        confidence=float(incident.confidence),
        detected_at=incident.detected_at,
        created_at=incident.created_at,
        timeline=timeline,
        affected_users=affected_users,
        affected_assets=affected_assets,
        events_count=len(incident.events),
    )


@router.get("/{incident_id}/attack-graph", response_model=AttackGraphResponse)
async def get_incident_attack_graph(
    incident_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate graph nodes and edges representing the entities and relationships of this attack chain.
    """
    stmt = (
        select(Incident)
        .options(selectinload(Incident.events))
        .where(Incident.id == incident_id)
    )
    res = await db.execute(stmt)
    incident = res.scalar_one_or_none()

    if not incident:
        raise NotFoundException("Incident", incident_id)

    return build_attack_graph(incident)


@router.patch("/{incident_id}/status", response_model=IncidentResponse)
async def update_incident_status(
    incident_id: str,
    payload: IncidentStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update incident status (OPEN, INVESTIGATING, CONTAINED, RESOLVED, CLOSED).
    """
    stmt = select(Incident).where(Incident.id == incident_id)
    res = await db.execute(stmt)
    incident = res.scalar_one_or_none()

    if not incident:
        raise NotFoundException("Incident", incident_id)

    old_status = incident.status
    incident.status = payload.status.upper()
    await db.commit()
    await db.refresh(incident)

    await log_audit_event(
        db=db,
        action="INCIDENT_STATUS_UPDATED",
        resource_type="INCIDENT",
        resource_id=incident.id,
        result="SUCCESS",
        actor_id=current_user.id,
        actor_email=current_user.email,
        metadata={"old_status": old_status, "new_status": incident.status},
    )

    return incident
