from typing import List
from app.models.event import SecurityEvent
from app.rules.base import BaseSecurityRule, RuleMatch
from app.rules.definitions import (
    BruteForceRule,
    CredentialExposureRule,
    ExcessiveApiRequestsRule,
    PrivilegeEscalationRule,
    SuspiciousDataAccessRule,
)


class RuleEngine:
    """
    Deterministic rule engine that coordinates security rule evaluations.
    """

    def __init__(self):
        self.rules: List[BaseSecurityRule] = [
            BruteForceRule(threshold=5, window_minutes=10),
            PrivilegeEscalationRule(),
            SuspiciousDataAccessRule(threshold=3, window_minutes=5),
            CredentialExposureRule(),
            ExcessiveApiRequestsRule(threshold=20, window_minutes=1),
        ]

    def register_rule(self, rule: BaseSecurityRule) -> None:
        self.rules.append(rule)

    def evaluate_event(
        self,
        current_event: SecurityEvent,
        historical_events: List[SecurityEvent],
    ) -> List[RuleMatch]:
        """
        Executes all active deterministic rules against the current event and historical context.
        """
        matches: List[RuleMatch] = []
        for rule in self.rules:
            match = rule.evaluate(current_event, historical_events)
            if match:
                matches.append(match)
        return matches


default_rule_engine = RuleEngine()
