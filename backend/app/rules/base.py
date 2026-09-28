from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.event import SecurityEvent


class RuleMatch(BaseModel):
    rule_id: str
    rule_name: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    actor: str
    source_ip: str
    evidence_event_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseSecurityRule(ABC):
    """
    Abstract deterministic security rule interface.
    """

    rule_id: str
    name: str
    severity: str
    description: str

    @abstractmethod
    def evaluate(
        self,
        current_event: SecurityEvent,
        historical_events: List[SecurityEvent],
    ) -> Optional[RuleMatch]:
        """
        Evaluates current event against recent historical context.
        Returns RuleMatch if rule conditions are satisfied, else None.
        """
        pass
