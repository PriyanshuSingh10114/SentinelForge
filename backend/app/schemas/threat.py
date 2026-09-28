from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ThreatModelCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=150)
    architecture_summary: str = Field(..., min_length=10, description="Description of components, boundaries, and data stores")


class ThreatItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    stride_category: str  # SPOOFING, TAMPERING, REPUDIATION, INFO_DISCLOSURE, DOS, ELEVATION
    target_component: str
    description: str
    mitigation: str
    status: str  # OPEN, MITIGATED, ACCEPTED, FALSE_POSITIVE


class ThreatModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    architecture_summary: str
    created_at: datetime
    items: List[ThreatItemResponse] = []


class ThreatItemStatusUpdateRequest(BaseModel):
    status: str = Field(..., description="OPEN, MITIGATED, ACCEPTED, FALSE_POSITIVE")
