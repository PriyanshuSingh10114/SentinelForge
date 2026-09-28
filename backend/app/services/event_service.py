from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundException
from app.models.event import SecurityEvent
from app.services.event_normalizer import normalize_security_event


async def ingest_single_event(
    db: AsyncSession,
    raw_payload: Dict[str, Any],
) -> SecurityEvent:
    core, normalized = normalize_security_event(raw_payload)

    event = SecurityEvent(
        event_type=core["event_type"],
        severity=core["severity"],
        source=core["source"],
        actor=core["actor"],
        source_ip=core["source_ip"],
        timestamp=core["timestamp"],
        raw_payload=raw_payload,
        normalized_payload=normalized,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event


async def ingest_batch_events(
    db: AsyncSession,
    events_raw: List[Dict[str, Any]],
) -> List[SecurityEvent]:
    persisted = []
    for raw in events_raw:
        core, normalized = normalize_security_event(raw)
        event = SecurityEvent(
            event_type=core["event_type"],
            severity=core["severity"],
            source=core["source"],
            actor=core["actor"],
            source_ip=core["source_ip"],
            timestamp=core["timestamp"],
            raw_payload=raw,
            normalized_payload=normalized,
        )
        db.add(event)
        persisted.append(event)

    await db.commit()
    for e in persisted:
        await db.refresh(e)
    return persisted


async def search_security_events(
    db: AsyncSession,
    severity: Optional[str] = None,
    event_type: Optional[str] = None,
    actor: Optional[str] = None,
    source_ip: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[int, List[SecurityEvent]]:
    """
    Search events with safe parameterized query filters.
    """
    query = select(SecurityEvent)
    count_query = select(func.count(SecurityEvent.id))

    if severity:
        query = query.where(SecurityEvent.severity == severity.upper())
        count_query = count_query.where(SecurityEvent.severity == severity.upper())
    if event_type:
        query = query.where(SecurityEvent.event_type == event_type.lower())
        count_query = count_query.where(SecurityEvent.event_type == event_type.lower())
    if actor:
        query = query.where(SecurityEvent.actor.ilike(f"%{actor}%"))
        count_query = count_query.where(SecurityEvent.actor.ilike(f"%{actor}%"))
    if source_ip:
        query = query.where(SecurityEvent.source_ip == source_ip)
        count_query = count_query.where(SecurityEvent.source_ip == source_ip)
    if from_date:
        query = query.where(SecurityEvent.timestamp >= from_date)
        count_query = count_query.where(SecurityEvent.timestamp >= from_date)
    if to_date:
        query = query.where(SecurityEvent.timestamp <= to_date)
        count_query = count_query.where(SecurityEvent.timestamp <= to_date)

    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0

    query = query.order_by(SecurityEvent.timestamp.desc()).offset(offset).limit(limit)
    res = await db.execute(query)
    items = list(res.scalars().all())

    return total, items


async def get_event_by_id(db: AsyncSession, event_id: str) -> SecurityEvent:
    stmt = select(SecurityEvent).where(SecurityEvent.id == event_id)
    res = await db.execute(stmt)
    event = res.scalar_one_or_none()
    if not event:
        raise NotFoundException("SecurityEvent", event_id)
    return event
