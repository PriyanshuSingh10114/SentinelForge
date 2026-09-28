from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PolicyCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=120)
    description: str = Field(..., min_length=5)
    policy_type: str = Field(..., description="DLP, RATE_LIMIT, ACCESS_CONTROL")
    configuration: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class PolicyResponse(BaseModel):
    id: str
    name: str
    description: str
    policy_type: str
    configuration: Dict[str, Any]
    enabled: bool


class AuditLogResponse(BaseModel):
    id: str
    actor_email: str
    action: str
    resource_type: str
    resource_id: str
    result: str
    metadata: Dict[str, Any]
    timestamp: str
