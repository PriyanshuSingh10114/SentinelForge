from datetime import datetime, timedelta, timezone
from app.models.event import SecurityEvent
from app.rules.engine import default_rule_engine


def make_event(
    event_type: str,
    actor: str = "dev_user",
    source_ip: str = "10.0.0.5",
    severity: str = "INFO",
    offset_seconds: int = 0,
    raw_payload: dict = None,
) -> SecurityEvent:
    now = datetime.now(timezone.utc) - timedelta(seconds=offset_seconds)
    return SecurityEvent(
        id=f"evt_{abs(offset_seconds)}_{event_type}",
        event_type=event_type,
        severity=severity,
        source="test_source",
        actor=actor,
        source_ip=source_ip,
        timestamp=now,
        raw_payload=raw_payload or {},
        normalized_payload={},
    )


def test_brute_force_rule_threshold():
    # 4 historical failed logins
    history = [
        make_event("failed_login", actor="attacker", offset_seconds=60),
        make_event("failed_login", actor="attacker", offset_seconds=120),
        make_event("failed_login", actor="attacker", offset_seconds=180),
        make_event("failed_login", actor="attacker", offset_seconds=240),
    ]

    # Current event is the 5th failed login
    current = make_event("failed_login", actor="attacker", offset_seconds=0)

    matches = default_rule_engine.evaluate_event(current, history)
    bf_matches = [m for m in matches if m.rule_id == "SEC-RULE-001"]
    assert len(bf_matches) == 1
    assert bf_matches[0].severity == "HIGH"
    assert len(bf_matches[0].evidence_event_ids) == 5

    # If only 3 historical (4 total) -> should NOT match
    matches_sub = default_rule_engine.evaluate_event(current, history[:3])
    bf_sub = [m for m in matches_sub if m.rule_id == "SEC-RULE-001"]
    assert len(bf_sub) == 0


def test_privilege_escalation_rule():
    current_unauthorized = make_event(
        "api_request",
        actor="junior_dev",
        raw_payload={"action": "UPDATE_POLICY", "resource": "/admin/policies"},
    )
    matches = default_rule_engine.evaluate_event(current_unauthorized, [])
    esc_matches = [m for m in matches if m.rule_id == "SEC-RULE-002"]
    assert len(esc_matches) == 1
    assert esc_matches[0].severity == "CRITICAL"

    # Legitimate admin performing same action should NOT trigger privilege escalation rule
    current_admin = make_event(
        "api_request",
        actor="admin@sentinelforge.local",
        raw_payload={"action": "UPDATE_POLICY", "resource": "/admin/policies"},
    )
    matches_admin = default_rule_engine.evaluate_event(current_admin, [])
    esc_admin = [m for m in matches_admin if m.rule_id == "SEC-RULE-002"]
    assert len(esc_admin) == 0


def test_suspicious_data_access_rule():
    history = [
        make_event("file_download", actor="rogue_user", offset_seconds=30, raw_payload={"classification": "RESTRICTED", "resource": "res_1"}),
        make_event("file_download", actor="rogue_user", offset_seconds=60, raw_payload={"classification": "CONFIDENTIAL", "resource": "res_2"}),
    ]
    current = make_event("file_download", actor="rogue_user", offset_seconds=0, raw_payload={"classification": "RESTRICTED", "resource": "res_3"})

    matches = default_rule_engine.evaluate_event(current, history)
    data_matches = [m for m in matches if m.rule_id == "SEC-RULE-003"]
    assert len(data_matches) == 1
    assert data_matches[0].severity == "HIGH"
    assert len(data_matches[0].metadata["distinct_resources"]) == 3


def test_credential_exposure_rule():
    current = make_event(
        "secret_detection",
        actor="committer_1",
        raw_payload={"matched_pattern": "AKIA****************MPLE", "data_type": "AWS_KEY"},
    )
    matches = default_rule_engine.evaluate_event(current, [])
    secret_matches = [m for m in matches if m.rule_id == "SEC-RULE-004"]
    assert len(secret_matches) == 1
    assert secret_matches[0].severity == "CRITICAL"


def test_excessive_api_requests_rule():
    ip = "198.51.100.25"
    history = [make_event("api_request", source_ip=ip, offset_seconds=i * 2) for i in range(1, 20)]
    current = make_event("api_request", source_ip=ip, offset_seconds=0)

    matches = default_rule_engine.evaluate_event(current, history)
    rate_matches = [m for m in matches if m.rule_id == "SEC-RULE-005"]
    assert len(rate_matches) == 1
    assert rate_matches[0].severity == "MEDIUM"
    assert rate_matches[0].metadata["request_count"] == 20
