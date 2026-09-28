from typing import Any, Dict, List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dlp.classifier import ClassifiedFinding, classify_text_content
from app.models.dlp import DlpFinding, SecurityPolicy


CLASSIFICATION_HIERARCHY = {
    "RESTRICTED": 4,
    "CONFIDENTIAL": 3,
    "INTERNAL": 2,
    "PUBLIC": 1,
}


def compute_overall_classification(findings: List[ClassifiedFinding]) -> str:
    if not findings:
        return "PUBLIC"
    highest_rank = 1
    highest_label = "PUBLIC"
    for f in findings:
        rank = CLASSIFICATION_HIERARCHY.get(f.classification, 1)
        if rank > highest_rank:
            highest_rank = rank
            highest_label = f.classification
    return highest_label


def evaluate_dlp_action(findings: List[ClassifiedFinding], policies: List[SecurityPolicy]) -> str:
    """
    Computes overall DLP action (BLOCK, QUARANTINE, WARN, ALLOW) based on findings and active policies.
    """
    if not findings:
        return "ALLOW"

    # Default baseline rules
    has_restricted = any(f.classification == "RESTRICTED" for f in findings)
    has_confidential = any(f.classification == "CONFIDENTIAL" for f in findings)

    # Check database policies if active
    for pol in policies:
        conf = pol.configuration or {}
        target_types = conf.get("target_types", [])
        pol_action = conf.get("action", "WARN")

        for f in findings:
            if f.data_type in target_types:
                if pol_action == "BLOCK":
                    return "BLOCK"
                if pol_action == "QUARANTINE":
                    return "QUARANTINE"

    if has_restricted:
        return "BLOCK"
    if has_confidential:
        return "WARN"

    return "ALLOW"


async def scan_and_record_dlp(
    db: AsyncSession,
    content: str,
    source_type: str = "PAYLOAD",
    source_id: str = "generic_source",
) -> Tuple[str, str, List[ClassifiedFinding], List[DlpFinding]]:
    """
    Scans content, applies DLP policies, and persists masked findings to the database.
    Returns (overall_classification, policy_action, findings, persisted_records).
    """
    findings = classify_text_content(content)

    # Fetch active DLP policies
    stmt = select(SecurityPolicy).where(SecurityPolicy.policy_type == "DLP", SecurityPolicy.enabled == True)
    res = await db.execute(stmt)
    policies = list(res.scalars().all())

    overall_classif = compute_overall_classification(findings)
    overall_action = evaluate_dlp_action(findings, policies)

    persisted_records: List[DlpFinding] = []
    for f in findings:
        # Determine individual action
        item_action = "BLOCK" if f.classification == "RESTRICTED" else ("WARN" if f.classification == "CONFIDENTIAL" else "ALLOW")
        record = DlpFinding(
            source_type=source_type,
            source_id=source_id,
            data_type=f.data_type,
            classification=f.classification,
            matched_pattern=f.matched_masked,  # Guaranteed masked
            confidence=f.confidence,
            action=item_action,
        )
        db.add(record)
        persisted_records.append(record)

    if persisted_records:
        await db.commit()
        for r in persisted_records:
            await db.refresh(r)

    return overall_classif, overall_action, findings, persisted_records
