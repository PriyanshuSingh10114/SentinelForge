from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.auth import User
from app.models.scan import ScanFinding
from app.security.dependencies import require_role

router = APIRouter(prefix="/scans", tags=["Security Scans"])


class ScanFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    scanner: str
    rule_id: str
    severity: str
    file_path: str
    line_number: Optional[int] = None
    description: str
    remediation: str
    status: str
    created_at: datetime


class IngestScanRequest(BaseModel):
    scanner: str = Field(..., description="Scanner name e.g., bandit, pip-audit, gitleaks, trivy")
    rule_id: str = Field(..., description="Finding rule ID e.g., B105, CVE-2024-1234")
    severity: str = Field(..., description="INFO, LOW, MEDIUM, HIGH, CRITICAL")
    file_path: str = Field(...)
    line_number: Optional[int] = None
    description: str = Field(...)
    remediation: str = Field(...)


@router.get("/findings", response_model=List[ScanFindingResponse])
async def list_scan_findings(
    scanner: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("VIEWER")),
):
    """
    List normalized SAST, SCA, and secret scan findings.
    """
    stmt = select(ScanFinding)
    if scanner:
        stmt = stmt.where(ScanFinding.scanner == scanner)
    if severity:
        stmt = stmt.where(ScanFinding.severity == severity.upper())
    if status:
        stmt = stmt.where(ScanFinding.status == status.upper())
    stmt = stmt.order_by(ScanFinding.created_at.desc())

    result = await db.execute(stmt)
    findings = result.scalars().all()
    return findings


@router.post("/ingest", response_model=ScanFindingResponse, status_code=status.HTTP_201_CREATED)
async def ingest_scan_finding(
    payload: IngestScanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("DEVELOPER")),
):
    """
    Ingest a security finding from DevSecOps CI/CD runners (SAST/SCA/Secret).
    """
    finding = ScanFinding(
        scanner=payload.scanner.lower(),
        rule_id=payload.rule_id,
        severity=payload.severity.upper(),
        file_path=payload.file_path,
        line_number=payload.line_number,
        description=payload.description,
        remediation=payload.remediation,
        status="OPEN",
    )
    db.add(finding)
    await db.commit()
    await db.refresh(finding)
    return finding
