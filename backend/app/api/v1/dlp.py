from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dlp.engine import scan_and_record_dlp
from app.models.auth import User
from app.models.dlp import DlpFinding
from app.schemas.dlp import DlpFindingResponse, DlpScanRequest, DlpScanResponse
from app.security.dependencies import get_current_user

router = APIRouter(prefix="/dlp", tags=["Data Loss Prevention & Classification"])


@router.post("/scan", response_model=DlpScanResponse, status_code=status.HTTP_200_OK)
async def scan_content(
    payload: DlpScanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Inspects text content, source code, or configuration for credentials, private keys, and PII.
    Applies DLP policy rules, masks findings, and returns deterministic classification and enforcement action.
    """
    classif, action, findings, _ = await scan_and_record_dlp(
        db=db,
        content=payload.content,
        source_type=payload.source_type,
        source_id=payload.source_id or f"user:{current_user.email}",
    )

    return DlpScanResponse(
        classification=classif,
        action=action,
        findings_count=len(findings),
        findings=findings,
    )


@router.get("/findings", response_model=List[DlpFindingResponse])
async def list_dlp_findings(
    data_type: Optional[str] = Query(None, description="AWS_ACCESS_KEY, EMAIL_PII, etc."),
    classification: Optional[str] = Query(None, description="CONFIDENTIAL, RESTRICTED"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List historical DLP detection findings with masked values.
    """
    query = select(DlpFinding).order_by(DlpFinding.created_at.desc())
    if data_type:
        query = query.where(DlpFinding.data_type == data_type)
    if classification:
        query = query.where(DlpFinding.classification == classification)

    query = query.offset(offset).limit(limit)
    res = await db.execute(query)
    findings = res.scalars().all()
    return findings
