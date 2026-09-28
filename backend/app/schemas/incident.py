from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TimelineItem(BaseModel):
    id: str
    timestamp: datetime
    event_type: str
    severity: str
    actor: str
    source_ip: str
    description: str


class AttackGraphNode(BaseModel):
    id: str
    label: str
    type: str  # USER, ASSET, CREDENTIAL, INCIDENT, API
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AttackGraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str


class AttackGraphResponse(BaseModel):
    nodes: List[AttackGraphNode]
    edges: List[AttackGraphEdge]


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_number: str
    title: str
    description: str
    severity: str
    status: str
    risk_score: int
    confidence: float
    detected_at: datetime
    created_at: datetime


class IncidentDetailResponse(IncidentResponse):
    risk_factors: List[Dict[str, Any]]
    timeline: List[TimelineItem]
    affected_users: List[str]
    affected_assets: List[str]
    events_count: int


class IncidentStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="OPEN, INVESTIGATING, CONTAINED, RESOLVED, CLOSED")
