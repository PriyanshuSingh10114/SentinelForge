import re
from typing import Any, Dict, List, Pattern

# High-precision deterministic regular expressions for credentials, secrets, and PII
DLP_PATTERNS: Dict[str, Dict[str, Any]] = {}

PATTERNS = [
    {
        "type": "AWS_ACCESS_KEY",
        "regex": re.compile(r"\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b"),
        "classification": "RESTRICTED",
        "confidence": 0.99,
        "reason": "Standard AWS IAM or STS Access Key ID format",
    },
    {
        "type": "GITHUB_PAT",
        "regex": re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,255}\b"),
        "classification": "RESTRICTED",
        "confidence": 0.98,
        "reason": "Standard GitHub Personal Access Token format",
    },
    {
        "type": "SLACK_WEBHOOK",
        "regex": re.compile(r"https:\/\/hooks\.slack\.com\/services\/T[a-zA-Z0-9_]+\/B[a-zA-Z0-9_]+\/[a-zA-Z0-9_]+"),
        "classification": "RESTRICTED",
        "confidence": 0.98,
        "reason": "Slack incoming webhook URL with embedded authentication token",
    },
    {
        "type": "PRIVATE_KEY",
        "regex": re.compile(r"-----BEGIN (?:RSA|EC|OPENSSH|DSA|PRIVATE) KEY-----"),
        "classification": "RESTRICTED",
        "confidence": 1.00,
        "reason": "Cryptographic private key PEM header",
    },
    {
        "type": "JWT_TOKEN",
        "regex": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9._-]{10,}\.[A-Za-z0-9._-]{10,}\b"),
        "classification": "CONFIDENTIAL",
        "confidence": 0.95,
        "reason": "JSON Web Token (JWT) bearer credential",
    },
    {
        "type": "DATABASE_URI",
        "regex": re.compile(r"(?:postgresql|postgres|mysql|mongodb|redis):\/\/[a-zA-Z0-9_]+:[^@\s]+@[a-zA-Z0-9_.-]+"),
        "classification": "RESTRICTED",
        "confidence": 0.97,
        "reason": "Database connection string containing embedded plaintext credentials",
    },
    {
        "type": "EMAIL_PII",
        "regex": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"),
        "classification": "CONFIDENTIAL",
        "confidence": 0.90,
        "reason": "Personally Identifiable Information: Electronic Mail Address",
    },
    {
        "type": "PHONE_NUMBER",
        "regex": re.compile(r"\b(?:\+?1[-. ]?)?\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})\b"),
        "classification": "CONFIDENTIAL",
        "confidence": 0.85,
        "reason": "Personally Identifiable Information: Contact Phone Number",
    },
]
