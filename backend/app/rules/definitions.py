from datetime import timedelta, timezone
from typing import List, Optional
from app.models.event import SecurityEvent
from app.rules.base import BaseSecurityRule, RuleMatch


class BruteForceRule(BaseSecurityRule):
    rule_id: str = "SEC-RULE-001"
    name: str = "Brute Force Authentication Attempt"
    severity: str = "HIGH"
    description: str = "Multiple failed authentication attempts detected within a 10-minute window."

    def __init__(self, threshold: int = 5, window_minutes: int = 10):
        self.threshold = threshold
        self.window = timedelta(minutes=window_minutes)

    def evaluate(
        self,
        current_event: SecurityEvent,
        historical_events: List[SecurityEvent],
    ) -> Optional[RuleMatch]:
        if current_event.event_type != "failed_login":
            return None

        now = current_event.timestamp
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        # Count failed logins matching same actor or source_ip within sliding window
        evidence = [current_event.id]
        for e in historical_events:
            if e.event_type == "failed_login":
                e_time = e.timestamp if e.timestamp.tzinfo else e.timestamp.replace(tzinfo=timezone.utc)
                if (now - e_time) <= self.window:
                    if e.actor == current_event.actor or e.source_ip == current_event.source_ip:
                        evidence.append(e.id)

        if len(evidence) >= self.threshold:
            return RuleMatch(
                rule_id=self.rule_id,
                rule_name=self.name,
                severity=self.severity,
                description=f"Detected {len(evidence)} failed authentication attempts within {self.window.total_seconds() / 60:.0f} minutes.",
                actor=current_event.actor,
                source_ip=current_event.source_ip,
                evidence_event_ids=evidence,
                metadata={"failed_attempts_count": len(evidence)},
            )
        return None


class PrivilegeEscalationRule(BaseSecurityRule):
    rule_id: str = "SEC-RULE-002"
    name: str = "Unauthorized Privilege Escalation Attempt"
    severity: str = "CRITICAL"
    description: str = "A low-privileged principal attempted to invoke an administrative or security-critical action."

    def evaluate(
        self,
        current_event: SecurityEvent,
        historical_events: List[SecurityEvent],
    ) -> Optional[RuleMatch]:
        payload = current_event.raw_payload or {}
        event_type = current_event.event_type.lower()

        is_escalation_type = any(
            t in event_type
            for t in ("privilege_escalation", "unauthorized_admin", "forbidden_access", "role_escalation")
        )
        is_admin_action = payload.get("action") in ("CREATE_ADMIN", "UPDATE_POLICY", "GRANT_ROLE", "DELETE_AUDIT")
        is_non_admin_actor = "admin" not in current_event.actor.lower()

        if (is_escalation_type or is_admin_action) and is_non_admin_actor:
            return RuleMatch(
                rule_id=self.rule_id,
                rule_name=self.name,
                severity=self.severity,
                description=f"Non-admin actor '{current_event.actor}' executed sensitive operation '{payload.get('action', event_type)}'.",
                actor=current_event.actor,
                source_ip=current_event.source_ip,
                evidence_event_ids=[current_event.id],
                metadata={"action": payload.get("action", event_type)},
            )
        return None


class SuspiciousDataAccessRule(BaseSecurityRule):
    rule_id: str = "SEC-RULE-003"
    name: str = "Suspicious Restricted Data Access"
    severity: str = "HIGH"
    description: str = "Principal accessed multiple restricted or confidential resources within a short duration."

    def __init__(self, threshold: int = 3, window_minutes: int = 5):
        self.threshold = threshold
        self.window = timedelta(minutes=window_minutes)

    def evaluate(
        self,
        current_event: SecurityEvent,
        historical_events: List[SecurityEvent],
    ) -> Optional[RuleMatch]:
        payload = current_event.raw_payload or {}
        classif = (payload.get("classification") or "").upper()
        if classif not in ("RESTRICTED", "CONFIDENTIAL") and current_event.event_type != "data_classification_event":
            return None

        now = current_event.timestamp
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        evidence = [current_event.id]
        accessed_resources = {payload.get("resource") or "unknown_resource"}

        for e in historical_events:
            e_payload = e.raw_payload or {}
            e_classif = (e_payload.get("classification") or "").upper()
            if e_classif in ("RESTRICTED", "CONFIDENTIAL") and e.actor == current_event.actor:
                e_time = e.timestamp if e.timestamp.tzinfo else e.timestamp.replace(tzinfo=timezone.utc)
                if (now - e_time) <= self.window:
                    evidence.append(e.id)
                    accessed_resources.add(e_payload.get("resource") or "unknown_resource")

        if len(accessed_resources) >= self.threshold or len(evidence) >= (self.threshold * 2):
            return RuleMatch(
                rule_id=self.rule_id,
                rule_name=self.name,
                severity=self.severity,
                description=f"Principal accessed {len(accessed_resources)} distinct sensitive resources ({len(evidence)} total operations) within 5 minutes.",
                actor=current_event.actor,
                source_ip=current_event.source_ip,
                evidence_event_ids=evidence,
                metadata={"distinct_resources": list(accessed_resources)},
            )
        return None


class CredentialExposureRule(BaseSecurityRule):
    rule_id: str = "SEC-RULE-004"
    name: str = "Exposed Credential Ingestion"
    severity: str = "CRITICAL"
    description: str = "Unmasked credentials or secrets detected inside telemetry payload."

    def evaluate(
        self,
        current_event: SecurityEvent,
        historical_events: List[SecurityEvent],
    ) -> Optional[RuleMatch]:
        if current_event.event_type in ("secret_detection", "secret_detected", "dlp_violation"):
            return RuleMatch(
                rule_id=self.rule_id,
                rule_name=self.name,
                severity=self.severity,
                description="Ingested telemetry indicates sensitive credential exposure in client payload.",
                actor=current_event.actor,
                source_ip=current_event.source_ip,
                evidence_event_ids=[current_event.id],
                metadata=current_event.raw_payload,
            )
        return None


class ExcessiveApiRequestsRule(BaseSecurityRule):
    rule_id: str = "SEC-RULE-005"
    name: str = "Excessive Request Rate Anomaly"
    severity: str = "MEDIUM"
    description: str = "Unusual surge of API requests detected from an individual source address."

    def __init__(self, threshold: int = 20, window_minutes: int = 1):
        self.threshold = threshold
        self.window = timedelta(minutes=window_minutes)

    def evaluate(
        self,
        current_event: SecurityEvent,
        historical_events: List[SecurityEvent],
    ) -> Optional[RuleMatch]:
        now = current_event.timestamp
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)

        evidence = [current_event.id]
        for e in historical_events:
            if e.source_ip == current_event.source_ip:
                e_time = e.timestamp if e.timestamp.tzinfo else e.timestamp.replace(tzinfo=timezone.utc)
                if (now - e_time) <= self.window:
                    evidence.append(e.id)

        if len(evidence) >= self.threshold:
            return RuleMatch(
                rule_id=self.rule_id,
                rule_name=self.name,
                severity=self.severity,
                description=f"Source IP '{current_event.source_ip}' issued {len(evidence)} requests within {self.window.total_seconds():.0f}s.",
                actor=current_event.actor,
                source_ip=current_event.source_ip,
                evidence_event_ids=evidence,
                metadata={"request_count": len(evidence)},
            )
        return None
