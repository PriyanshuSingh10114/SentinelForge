import re
from datetime import datetime, timezone
from typing import Any, Dict, Tuple


VALID_SEVERITIES = {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}
IP_REGEX = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$|^[a-fA-F0-9:]+$")


def parse_timestamp(val: Any) -> datetime:
    if isinstance(val, datetime):
        return val if val.tzinfo else val.replace(tzinfo=timezone.utc)
    if isinstance(val, (int, float)):
        # Epoch timestamp
        return datetime.fromtimestamp(val, tz=timezone.utc)
    if isinstance(val, str) and val.strip():
        clean_val = val.strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(clean_val)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def normalize_security_event(raw: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Normalizes a heterogeneous raw security event into canonical attributes.
    Returns (core_attributes, normalized_payload).
    """
    # 1. Normalize Actor / Principal
    actor_candidates = [
        raw.get("user"),
        raw.get("username"),
        raw.get("principal"),
        raw.get("actor"),
        raw.get("user_id"),
        raw.get("email"),
        raw.get("sub"),
    ]
    actor = next((str(c).strip() for c in actor_candidates if c is not None and str(c).strip()), "anonymous")

    # 2. Normalize Source IP
    ip_candidates = [
        raw.get("source_ip"),
        raw.get("client_ip"),
        raw.get("remote_addr"),
        raw.get("ip"),
        raw.get("src_ip"),
    ]
    raw_ip = next((str(c).strip() for c in ip_candidates if c is not None and str(c).strip()), "127.0.0.1")
    source_ip = raw_ip if IP_REGEX.match(raw_ip) else "127.0.0.1"

    # 3. Normalize Event Type
    type_candidates = [
        raw.get("event_type"),
        raw.get("type"),
        raw.get("action_type"),
        raw.get("event_name"),
    ]
    raw_type = next((str(c).strip().lower() for c in type_candidates if c is not None and str(c).strip()), "generic_event")
    event_type = re.sub(r"[^a-z0-9_]", "_", raw_type)[:80]

    # 4. Normalize Severity
    sev_candidates = [
        raw.get("severity"),
        raw.get("level"),
        raw.get("priority"),
    ]
    raw_sev = next((str(c).strip().upper() for c in sev_candidates if c is not None and str(c).strip()), "INFO")
    severity = raw_sev if raw_sev in VALID_SEVERITIES else "INFO"

    # 5. Normalize Source
    source = str(raw.get("source") or "external_ingest").strip()[:80]

    # 6. Normalize Timestamp
    timestamp = parse_timestamp(raw.get("timestamp"))

    # 7. Normalize Resource and Action
    resource = str(raw.get("resource") or raw.get("target") or raw.get("asset") or "").strip()
    action = str(raw.get("action") or raw.get("operation") or "").strip().upper()

    core = {
        "event_type": event_type,
        "severity": severity,
        "source": source,
        "actor": actor,
        "source_ip": source_ip,
        "timestamp": timestamp,
    }

    normalized_payload = {
        "event_type": event_type,
        "severity": severity,
        "source": source,
        "actor": actor,
        "source_ip": source_ip,
        "timestamp": timestamp.isoformat(),
        "resource": resource,
        "action": action,
        "details": {k: v for k, v in raw.items() if k not in ("password", "secret", "token")},
    }

    return core, normalized_payload
