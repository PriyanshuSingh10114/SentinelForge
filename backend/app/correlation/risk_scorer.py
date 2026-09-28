from typing import Any, Dict, List, Tuple
from pydantic import BaseModel


class RiskFactor(BaseModel):
    name: str
    points: int
    reason: str


def calculate_risk_score(
    events: List[Any],
    has_restricted_data: bool = False,
    is_privileged_account: bool = False,
    is_brute_force: bool = False,
    has_credential_exposure: bool = False,
    correlated_event_count: int = 1,
) -> Tuple[int, str, List[Dict[str, Any]]]:
    """
    Computes an explainable, transparent risk score (0-100) and severity category.
    Returns (score, severity, risk_factors_list).
    """
    factors: List[RiskFactor] = []
    total_points = 0

    # 1. Restricted / Confidential Data Involved
    if has_restricted_data:
        pts = 25
        total_points += pts
        factors.append(RiskFactor(name="Data Sensitivity", points=pts, reason="+25 Restricted or confidential data involved in incident"))

    # 2. Privileged Account Targeted or Involved
    if is_privileged_account:
        pts = 20
        total_points += pts
        factors.append(RiskFactor(name="Account Privilege", points=pts, reason="+20 Administrative or privileged account involved"))

    # 3. Repeated Failed Authentication / Brute Force
    if is_brute_force:
        pts = 20
        total_points += pts
        factors.append(RiskFactor(name="Authentication Velocity", points=pts, reason="+20 Repeated failed authentication attempts detected"))

    # 4. Credential / Secret Exposure
    if has_credential_exposure:
        pts = 20
        total_points += pts
        factors.append(RiskFactor(name="Credential Compromise", points=pts, reason="+20 Unmasked credentials or secrets exposed"))

    # 5. Correlated Event Density
    if correlated_event_count > 1:
        pts = min(15, correlated_event_count * 3)
        total_points += pts
        factors.append(RiskFactor(name="Attack Chain Correlation", points=pts, reason=f"+{pts} High correlation across {correlated_event_count} related security events"))

    # Base severity from event levels
    severities = [getattr(e, "severity", "INFO") for e in events]
    if "CRITICAL" in severities:
        total_points += 15
        factors.append(RiskFactor(name="Critical Event Telemetry", points=15, reason="+15 Raw telemetry includes CRITICAL severity indicator"))
    elif "HIGH" in severities:
        total_points += 10
        factors.append(RiskFactor(name="High Event Telemetry", points=10, reason="+10 Raw telemetry includes HIGH severity indicator"))

    final_score = min(100, max(10, total_points))

    if final_score >= 90:
        severity = "CRITICAL"
    elif final_score >= 70:
        severity = "HIGH"
    elif final_score >= 40:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    return final_score, severity, [f.model_dump() for f in factors]
