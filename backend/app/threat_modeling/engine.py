from typing import Any, Dict, List
from pydantic import BaseModel


class GeneratedThreat(BaseModel):
    stride_category: str  # SPOOFING, TAMPERING, REPUDIATION, INFO_DISCLOSURE, DOS, ELEVATION
    target_component: str
    description: str
    mitigation: str


COMPONENT_THREAT_TEMPLATES = {
    "auth": [
        GeneratedThreat(
            stride_category="SPOOFING",
            target_component="Authentication Provider",
            description="Attacker performs automated credential stuffing or password spray attacks against authentication endpoints.",
            mitigation="Enforce progressive rate limiting, account lockout thresholds, and multi-factor authentication (MFA).",
        ),
        GeneratedThreat(
            stride_category="ELEVATION",
            target_component="Authentication Provider",
            description="Attacker exploits weak signing secrets or token confusion to forge administrative JWT claims.",
            mitigation="Sign JWTs using high-entropy 256-bit secrets, enforce strict expiration (15-30m), and check revocation status in Redis.",
        ),
    ],
    "api": [
        GeneratedThreat(
            stride_category="DOS",
            target_component="API Gateway",
            description="Adversary issues high-volume volumetric HTTP floods to exhaust backend server resources and connection pools.",
            mitigation="Deploy edge rate limiting, enforce client payload size caps, and implement IP-based throttling.",
        ),
        GeneratedThreat(
            stride_category="ELEVATION",
            target_component="API Gateway",
            description="Broken Object Level Authorization (BOLA/IDOR) allows low-privileged users to query or mutate resources of other tenants.",
            mitigation="Enforce server-side tenancy verification and role-based access control (RBAC) middleware on every endpoint.",
        ),
    ],
    "database": [
        GeneratedThreat(
            stride_category="TAMPERING",
            target_component="Database Tier",
            description="SQL Injection via untrusted search parameters allows unauthorized database record modifications.",
            mitigation="Use SQLAlchemy ORM parameterized queries exclusively. Prohibit raw SQL string concatenation.",
        ),
        GeneratedThreat(
            stride_category="INFO_DISCLOSURE",
            target_component="Database Tier",
            description="Unencrypted database backups or database connection strings leak customer PII and credentials.",
            mitigation="Enable AWS KMS / AES-256 encryption at rest; mask secrets immediately upon detection; use VPC private subnets.",
        ),
    ],
    "storage": [
        GeneratedThreat(
            stride_category="INFO_DISCLOSURE",
            target_component="Object Storage (S3)",
            description="Misconfigured public S3 bucket policies expose confidential customer documents to the public internet.",
            mitigation="Enable S3 Block Public Access at the account and bucket level; enforce encrypted bucket policies.",
        ),
        GeneratedThreat(
            stride_category="TAMPERING",
            target_component="Object Storage (S3)",
            description="Malicious user overwrites critical data files or injects malicious payloads into uploaded artifacts.",
            mitigation="Enable S3 Object Versioning and strict IAM upload write restrictions.",
        ),
    ],
    "logging": [
        GeneratedThreat(
            stride_category="REPUDIATION",
            target_component="Audit Logging Subsystem",
            description="Compromised administrator deletes or modifies audit log entries to conceal unauthorized actions.",
            mitigation="Implement append-only audit log tables without application-level DELETE or UPDATE grants; stream to CloudWatch.",
        ),
    ],
}


def analyze_architecture_and_generate_threats(
    architecture_summary: str,
) -> List[GeneratedThreat]:
    """
    Parses application architecture description and produces mapped STRIDE threats and mitigations.
    """
    summary_lower = architecture_summary.lower()
    threats: List[GeneratedThreat] = []

    # Map architecture keywords to STRIDE threat templates
    keywords_matched = set()
    if any(k in summary_lower for k in ("auth", "login", "jwt", "token", "identity")):
        threats.extend(COMPONENT_THREAT_TEMPLATES["auth"])
        keywords_matched.add("auth")

    if any(k in summary_lower for k in ("api", "gateway", "backend", "fastapi", "rest")):
        threats.extend(COMPONENT_THREAT_TEMPLATES["api"])
        keywords_matched.add("api")

    if any(k in summary_lower for k in ("db", "database", "postgres", "sql", "data")):
        threats.extend(COMPONENT_THREAT_TEMPLATES["database"])
        keywords_matched.add("database")

    if any(k in summary_lower for k in ("s3", "storage", "bucket", "file", "upload")):
        threats.extend(COMPONENT_THREAT_TEMPLATES["storage"])
        keywords_matched.add("storage")

    if any(k in summary_lower for k in ("log", "audit", "trail", "monitor", "telemetry")):
        threats.extend(COMPONENT_THREAT_TEMPLATES["logging"])
        keywords_matched.add("logging")

    # If generic or no specific match, provide comprehensive baseline covering all STRIDE categories
    if not threats or len(keywords_matched) < 3:
        all_threats = []
        for group in COMPONENT_THREAT_TEMPLATES.values():
            all_threats.extend(group)
        return all_threats

    return threats
