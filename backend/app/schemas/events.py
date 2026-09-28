from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class RawEventIngestRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_type: Optional[str] = None
    severity: Optional[str] = None
    source: Optional[str] = "external"
    timestamp: Optional[str] = None


class BatchEventIngestRequest(BaseModel):
    events: List[Dict[str, Any]] = Field(..., min_length=1, max_length=100)


class NormalizedEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: str
    severity: str
    source: str
    actor: str
    source_ip: str
    timestamp: datetime
    raw_payload: Dict[str, Any]
    normalized_payload: Dict[str, Any]
    created_at: datetime


class EventSearchResponse(BaseModel):
    total: int
    items: List[NormalizedEventResponse]
