from typing import Any, Dict, List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agent import SecurityInvestigatorGraph
from app.ai.schemas import InvestigationReportOutput
from app.core.errors import NotFoundException
from app.models.incident import Incident, InvestigationReport, RemediationAction
from app.services.audit_service import log_audit_event


async def run_incident_investigation(
    db: AsyncSession,
    incident_id: str,
    analyst_user_id: str,
    analyst_email: str,
    analyst_role: str = "Analyst",
) -> Tuple[InvestigationReport, List[RemediationAction]]:
    """
    Executes the LangGraph AI investigator on an incident, persists the investigation report,
    and stages recommended remediation actions in PENDING_APPROVAL status.
    """
    stmt = select(Incident).where((Incident.id == incident_id) | (Incident.incident_number == incident_id))
    res = await db.execute(stmt)
    incident = res.scalar_one_or_none()
    if not incident:
        raise NotFoundException("Incident", incident_id)

    # 1. Execute LangGraph investigator
    investigator = SecurityInvestigatorGraph(db=db)
    report_output: InvestigationReportOutput = await investigator.run(
        incident_id=incident.id, user_role=analyst_role
    )

    # 2. Persist InvestigationReport
    db_report = InvestigationReport(
        incident_id=incident.id,
        summary=report_output.incident_summary,
        attack_chain=[s.model_dump() for s in report_output.attack_chain],
        evidence=[f.model_dump() for f in report_output.evidence_facts],
        findings=[f.model_dump() for f in report_output.findings],
        recommendations=[r.model_dump() for r in report_output.recommendations],
        confidence=report_output.confidence,
        model_used=report_output.model_used,
        created_by=analyst_user_id,
    )
    db.add(db_report)

    # 3. Stage Remediation Actions in PENDING_APPROVAL status
    persisted_actions: List[RemediationAction] = []
    for rec in report_output.recommendations:
        action = RemediationAction(
            incident_id=incident.id,
            action_type=rec.action_type,
            description=f"{rec.description} (Target: {rec.target}). Impact: {rec.impact}",
            status="PENDING_APPROVAL",  # NEVER execute without human approval
            requested_by=analyst_user_id,
        )
        db.add(action)
        persisted_actions.append(action)

    await db.commit()
    await db.refresh(db_report)
    for a in persisted_actions:
        await db.refresh(a)

    # 4. Audit Log
    await log_audit_event(
        db=db,
        action="AI_INVESTIGATION_COMPLETED",
        resource_type="INCIDENT",
        resource_id=incident.id,
        result="SUCCESS",
        actor_id=analyst_user_id,
        actor_email=analyst_email,
        metadata={"model": report_output.model_used, "recommendations_count": len(persisted_actions)},
    )

    return db_report, persisted_actions
