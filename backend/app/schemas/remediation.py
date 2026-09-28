from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field


class RemediationActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    action_type: str
    description: str
    status: str  # PENDING_APPROVAL, APPROVED, REJECTED, EXECUTED, FAILED
    requested_by: Optional[str] = None
    approved_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    executed_at: Optional[datetime] = None
    created_at: datetime


class RemediationApprovalRequest(BaseModel):
    notes: Optional[str] = Field(default=None, description="Admin approval notes")


class RemediationRejectionRequest(BaseModel):
    reason: str = Field(..., min_length=3, description="Justification for rejecting the remediation action")
