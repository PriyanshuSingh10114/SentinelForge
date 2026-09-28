from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.remediation import RemediationActionResponse


class InvestigationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    summary: str
    attack_chain: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    findings: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    confidence: float
    model_used: str
    created_at: datetime
    pending_remediations: List[RemediationActionResponse] = []
