from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.dlp.entropy import calculate_shannon_entropy
from app.dlp.masking import mask_connection_string, mask_secret
from app.dlp.patterns import PATTERNS


class ClassifiedFinding(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    data_type: str
    classification: str  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    matched_masked: str  # NEVER store or return plaintext
    confidence: float
    start_index: int
    end_index: int
    reason: str


def classify_text_content(content: str) -> List[ClassifiedFinding]:
    """
    Scans input text for sensitive patterns and high-entropy secrets.
    Masks every matched secret immediately before returning.
    """
    findings: List[ClassifiedFinding] = []
    if not content:
        return findings

    # 1. Pattern Regex Evaluation
    for p in PATTERNS:
        regex = p["regex"]
        for match in regex.finditer(content):
            raw_match = match.group(0)
            start, end = match.span()

            if p["type"] == "DATABASE_URI":
                masked = mask_connection_string(raw_match)
            elif p["type"] in ("EMAIL_PII", "PHONE_NUMBER"):
                # Mask middle of email / phone
                if "@" in raw_match:
                    parts = raw_match.split("@")
                    masked = f"{parts[0][:2]}***@{parts[1]}"
                else:
                    masked = f"{raw_match[:3]}***{raw_match[-2:]}"
            else:
                masked = mask_secret(raw_match)

            findings.append(
                ClassifiedFinding(
                    data_type=p["type"],
                    classification=p["classification"],
                    matched_masked=masked,
                    confidence=p["confidence"],
                    start_index=start,
                    end_index=end,
                    reason=p["reason"],
                )
            )

    # 2. Shannon Entropy Heuristic Evaluation
    # Inspect individual word tokens > 20 characters for high entropy
    words = content.split()
    for word in words:
        clean_word = word.strip("=;:'\", \t\r\n")
        if len(clean_word) >= 24 and not any(f.matched_masked.startswith(clean_word[:4]) for f in findings):
            entropy = calculate_shannon_entropy(clean_word)
            if entropy >= 4.5:
                # Find occurrence in content
                idx = content.find(clean_word)
                findings.append(
                    ClassifiedFinding(
                        data_type="HIGH_ENTROPY_SECRET",
                        classification="RESTRICTED",
                        matched_masked=mask_secret(clean_word),
                        confidence=0.88,
                        start_index=idx if idx != -1 else 0,
                        end_index=(idx + len(clean_word)) if idx != -1 else len(clean_word),
                        reason=f"High Shannon entropy token ({entropy} bits/char) indicates potential random key/token",
                    )
                )

    return findings
