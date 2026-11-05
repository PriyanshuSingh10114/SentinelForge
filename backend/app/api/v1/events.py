from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.auth import User
from app.models.event import SecurityEvent
from app.schemas.events import (
    BatchEventIngestRequest,
    EventSearchResponse,
    NormalizedEventResponse,
)
from app.security.dependencies import get_current_user
from app.services.event_service import (
    get_event_by_id,
    ingest_batch_events,
    ingest_single_event,
    search_security_events,
)

router = APIRouter(prefix="/events", tags=["Security Events"])


@router.post(
    "",
    response_model=NormalizedEventResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def ingest_event(
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    """
    Ingest a heterogeneous security event.
    Automatically extracts and normalizes principal, network indicators, severity, and event type.
    """
    event = await ingest_single_event(db=db, raw_payload=payload)
    return event


@router.post(
    "/batch",
    response_model=List[NormalizedEventResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def ingest_batch(
    payload: BatchEventIngestRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    High-throughput batch ingestion for log forwarders and scanners (up to 100 events per request).
    """
    events = await ingest_batch_events(db=db, events_raw=payload.events)
    return events


@router.get(
    "",
    response_model=EventSearchResponse,
    dependencies=[Depends(get_current_user)],
)
async def list_security_events(
    severity: Optional[str] = Query(None, description="INFO, LOW, MEDIUM, HIGH, CRITICAL"),
    event_type: Optional[str] = Query(None, description="login, failed_login, file_access, etc."),
    actor: Optional[str] = Query(None, description="Filter by actor/username"),
    source_ip: Optional[str] = Query(None, description="Source IPv4/IPv6"),
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Search and filter normalized security events using safe parameterized queries.
    """
    total, items = await search_security_events(
        db=db,
        severity=severity,
        event_type=event_type,
        actor=actor,
        source_ip=source_ip,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
    return EventSearchResponse(total=total, items=items)


@router.post(
    "/simulate",
    response_model=List[NormalizedEventResponse],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
async def generate_simulated_events(
    db: AsyncSession = Depends(get_db),
):
    """
    Explicitly generate controlled simulated security events for testing and demonstration.
    All events are tagged with provenance metadata (is_simulated=True, source=simulated_generator).
    """
    now = datetime.now(timezone.utc)
    demo_events = [
        SecurityEvent(
            event_type="failed_login",
            severity="MEDIUM",
            source="simulated_generator",
            actor="adversary_sim",
            source_ip="198.51.100.42",
            timestamp=now,
            raw_payload={"attempt": 1, "is_simulated": True, "simulation_source": "demo_generator"},
            normalized_payload={"is_simulated": True, "source_type": "simulated", "description": "Simulated brute force attempt"},
        ),
        SecurityEvent(
            event_type="failed_login",
            severity="MEDIUM",
            source="simulated_generator",
            actor="adversary_sim",
            source_ip="198.51.100.42",
            timestamp=now,
            raw_payload={"attempt": 2, "is_simulated": True, "simulation_source": "demo_generator"},
            normalized_payload={"is_simulated": True, "source_type": "simulated", "description": "Simulated brute force attempt"},
        ),
        SecurityEvent(
            event_type="privilege_escalation",
            severity="CRITICAL",
            source="simulated_generator",
            actor="adversary_sim",
            source_ip="198.51.100.42",
            timestamp=now,
            raw_payload={"resource": "arn:aws:iam::123456789012:role/AdminRole", "action": "iam:AttachRolePolicy", "is_simulated": True},
            normalized_payload={"is_simulated": True, "source_type": "simulated", "description": "Simulated IAM privilege escalation"},
        ),
    ]
    db.add_all(demo_events)
    await db.commit()
    for e in demo_events:
        await db.refresh(e)
    return demo_events


@router.get(
    "/{event_id}",
    response_model=NormalizedEventResponse,
    dependencies=[Depends(get_current_user)],
)
async def get_event(
    event_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve single security event by UUID.
    """
    event = await get_event_by_id(db=db, event_id=event_id)
    return event
