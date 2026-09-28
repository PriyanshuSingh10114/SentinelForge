import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.correlation.risk_scorer import calculate_risk_score
from app.models.event import SecurityEvent
from app.models.incident import Incident
from app.schemas.incident import (
    AttackGraphEdge,
    AttackGraphNode,
    AttackGraphResponse,
    TimelineItem,
)


def generate_incident_number() -> str:
    short_id = uuid.uuid4().hex[:6].upper()
    return f"INC-{short_id}"


def build_attack_graph(incident: Incident) -> AttackGraphResponse:
    nodes: Dict[str, AttackGraphNode] = {}
    edges: List[AttackGraphEdge] = []

    # Incident Node
    inc_node_id = f"inc_{incident.id}"
    nodes[inc_node_id] = AttackGraphNode(
        id=inc_node_id,
        label=incident.incident_number,
        type="INCIDENT",
        metadata={"title": incident.title, "severity": incident.severity, "score": incident.risk_score},
    )

    for idx, e in enumerate(incident.events):
        actor_id = f"user_{e.actor}"
        if actor_id not in nodes:
            nodes[actor_id] = AttackGraphNode(
                id=actor_id,
                label=e.actor,
                type="USER",
                metadata={"source_ip": e.source_ip},
            )
            # Edge from User to Incident
            edges.append(
                AttackGraphEdge(
                    id=f"edge_usr_inc_{e.actor}",
                    source=actor_id,
                    target=inc_node_id,
                    label="implicated_in",
                )
            )

        # Check payload resources
        payload = e.raw_payload or {}
        resource = payload.get("resource")
        if resource:
            res_id = f"res_{resource}"
            if res_id not in nodes:
                nodes[res_id] = AttackGraphNode(
                    id=res_id,
                    label=resource,
                    type="ASSET",
                    metadata={"classification": payload.get("classification", "INTERNAL")},
                )
            edges.append(
                AttackGraphEdge(
                    id=f"edge_{actor_id}_{res_id}_{idx}",
                    source=actor_id,
                    target=res_id,
                    label=payload.get("action", e.event_type),
                )
            )

        # Check secret or credential
        if e.event_type in ("secret_detection", "dlp_violation"):
            cred_id = f"cred_{e.id}"
            nodes[cred_id] = AttackGraphNode(
                id=cred_id,
                label="Exposed Credential",
                type="CREDENTIAL",
                metadata={"pattern": payload.get("matched_pattern", "MASKED")},
            )
            edges.append(
                AttackGraphEdge(
                    id=f"edge_cred_{idx}",
                    source=actor_id,
                    target=cred_id,
                    label="exposed",
                )
            )

    return AttackGraphResponse(nodes=list(nodes.values()), edges=edges)


def build_timeline(incident: Incident) -> List[TimelineItem]:
    # Sort events chronologically
    sorted_events = sorted(incident.events, key=lambda e: e.timestamp)
    timeline: List[TimelineItem] = []

    for e in sorted_events:
        payload = e.raw_payload or {}
        desc = (
            payload.get("description")
            or f"Action '{payload.get('action', e.event_type)}' on resource '{payload.get('resource', 'N/A')}'"
        )
        timeline.append(
            TimelineItem(
                id=e.id,
                timestamp=e.timestamp,
                event_type=e.event_type,
                severity=e.severity,
                actor=e.actor,
                source_ip=e.source_ip,
                description=desc,
            )
        )
    return timeline


async def correlate_events_into_incident(
    db: AsyncSession,
    events: List[SecurityEvent],
    title: Optional[str] = None,
    description: Optional[str] = None,
) -> Incident:
    """
    Correlates a cluster of related events into a formalized Incident with explainable risk scoring.
    """
    if not events:
        raise ValueError("Cannot correlate empty event set")

    # Detect risk factors
    has_restricted = False
    is_privileged = False
    is_brute_force = False
    has_credential_exposure = False

    for e in events:
        payload = e.raw_payload or {}
        classif = (payload.get("classification") or "").upper()
        if classif in ("RESTRICTED", "CONFIDENTIAL"):
            has_restricted = True
        if "admin" in e.actor.lower() or payload.get("action") in ("CREATE_ADMIN", "UPDATE_POLICY"):
            is_privileged = True
        if e.event_type == "failed_login":
            is_brute_force = True
        if e.event_type in ("secret_detection", "dlp_violation"):
            has_credential_exposure = True

    score, severity, factors = calculate_risk_score(
        events=events,
        has_restricted_data=has_restricted,
        is_privileged_account=is_privileged,
        is_brute_force=is_brute_force,
        has_credential_exposure=has_credential_exposure,
        correlated_event_count=len(events),
    )

    inc_num = generate_incident_number()
    inc_title = title or f"Suspicious Activity Cluster on Actor '{events[0].actor}'"
    inc_desc = (
        description
        or f"Correlated {len(events)} security events involving {len(set(e.actor for e in events))} actors and {len(set(e.source_ip for e in events))} IP addresses."
    )

    earliest_time = min(e.timestamp for e in events)

    incident = Incident(
        incident_number=inc_num,
        title=inc_title,
        description=inc_desc,
        severity=severity,
        status="OPEN",
        risk_score=score,
        risk_factors=factors,
        confidence=0.92,
        detected_at=earliest_time,
        events=events,
    )

    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident
