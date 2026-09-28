from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.dlp.classifier import ClassifiedFinding


class DlpScanRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=500000, description="Text or configuration content to inspect")
    source_type: str = Field(default="PAYLOAD", description="PAYLOAD, FILE_UPLOAD, GIT_COMMIT")
    source_id: Optional[str] = Field(default="manual_scan", description="Identifier of source asset or file")


class DlpFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    source_type: str
    source_id: str
    data_type: str
    classification: str
    matched_pattern: str  # Always masked
    confidence: float
    action: str
    created_at: datetime


class DlpScanResponse(BaseModel):
    classification: str  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    action: str  # ALLOW, WARN, BLOCK, QUARANTINE
    findings_count: int
    findings: List[ClassifiedFinding]
