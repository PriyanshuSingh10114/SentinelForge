from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FactEvidence(BaseModel):
    event_id: str
    fact: str
    timestamp: str


class FindingItem(BaseModel):
    category: str
    severity: str
    inference: str
    evidence_refs: List[str] = Field(default_factory=list)


class AttackChainStep(BaseModel):
    step_number: int
    stage_name: str
    actor: str
    action: str
    resource: Optional[str] = None
    timestamp: str


class RecommendationItem(BaseModel):
    action_type: str  # DISABLE_USER, REVOKE_TOKEN, ISOLATE_ASSET, ROTATE_CREDENTIAL
    target: str
    description: str
    impact: str
    requires_human_approval: bool = True
    suggested_by: str = "AI_INVESTIGATOR"


class InvestigationReportOutput(BaseModel):
    incident_summary: str
    severity: str
    confidence: float
    attack_chain: List[AttackChainStep]
    evidence_facts: List[FactEvidence]
    findings: List[FindingItem]
    recommendations: List[RecommendationItem]
    requires_human_approval: bool = True
    model_used: str = "gpt-4o-mini-orchestrated"
