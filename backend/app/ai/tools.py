from typing import Any, Dict, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.asset import Asset
from app.models.audit import AuditLog
from app.models.auth import User
from app.models.dlp import DlpFinding, SecurityPolicy
from app.models.event import SecurityEvent
from app.models.incident import Incident


class AgentTools:
    """
    Read-only inspection tools available to the LangGraph AI Investigator.
    Enforces deterministic safety: no mutation or destructive methods exist in this class.
    """

    @staticmethod
    async def get_incident(db: AsyncSession, incident_id: str) -> Optional[Dict[str, Any]]:
        stmt = (
            select(Incident)
            .options(selectinload(Incident.events))
            .where((Incident.id == incident_id) | (Incident.incident_number == incident_id))
        )
        res = await db.execute(stmt)
        inc = res.scalar_one_or_none()
        if not inc:
            return None
        return {
            "id": inc.id,
            "incident_number": inc.incident_number,
            "title": inc.title,
            "severity": inc.severity,
            "status": inc.status,
            "risk_score": inc.risk_score,
            "risk_factors": inc.risk_factors,
            "events_count": len(inc.events),
            "events": [
                {
                    "id": e.id,
                    "event_type": e.event_type,
                    "severity": e.severity,
                    "actor": e.actor,
                    "source_ip": e.source_ip,
                    "timestamp": e.timestamp.isoformat(),
                    "resource": (e.raw_payload or {}).get("resource", "N/A"),
                    "action": (e.raw_payload or {}).get("action", e.event_type),
                    "raw_payload": e.raw_payload,
                }
                for e in inc.events
            ],
        }

    @staticmethod
    async def search_security_events(
        db: AsyncSession,
        actor: Optional[str] = None,
        source_ip: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        query = select(SecurityEvent).order_by(SecurityEvent.timestamp.desc()).limit(limit)
        if actor:
            query = query.where(SecurityEvent.actor == actor)
        if source_ip:
            query = query.where(SecurityEvent.source_ip == source_ip)
        res = await db.execute(query)
        events = res.scalars().all()
        return [
            {
                "id": e.id,
                "event_type": e.event_type,
                "severity": e.severity,
                "actor": e.actor,
                "source_ip": e.source_ip,
                "timestamp": e.timestamp.isoformat(),
                "resource": (e.raw_payload or {}).get("resource", "N/A"),
                "action": (e.raw_payload or {}).get("action", e.event_type),
            }
            for e in events
        ]

    @staticmethod
    async def get_user_activity(db: AsyncSession, actor: str) -> Dict[str, Any]:
        stmt = select(SecurityEvent).where(SecurityEvent.actor == actor).order_by(SecurityEvent.timestamp.desc()).limit(30)
        res = await db.execute(stmt)
        events = res.scalars().all()
        failed_logins = sum(1 for e in events if e.event_type == "failed_login")
        file_accesses = sum(1 for e in events if "file" in e.event_type)
        return {
            "actor": actor,
            "total_recent_events": len(events),
            "failed_logins_count": failed_logins,
            "file_accesses_count": file_accesses,
            "unique_ips": list(set(e.source_ip for e in events)),
        }

    @staticmethod
    async def get_user_permissions(db: AsyncSession, actor: str) -> Dict[str, Any]:
        stmt = select(User).where((User.email == actor) | (User.name == actor))
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()
        if not user:
            return {"actor": actor, "is_registered": False, "role": "EXTERNAL_UNKNOWN", "permissions": []}
        return {
            "actor": actor,
            "is_registered": True,
            "role": user.role.name if user.role else "Viewer",
            "is_active": user.is_active,
            "permissions": [p.name for p in user.role.permissions] if user.role else [],
        }

    @staticmethod
    async def get_dlp_findings(db: AsyncSession, source_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = select(DlpFinding).order_by(DlpFinding.created_at.desc()).limit(15)
        if source_id:
            query = query.where(DlpFinding.source_id == source_id)
        res = await db.execute(query)
        findings = res.scalars().all()
        return [
            {
                "id": f.id,
                "data_type": f.data_type,
                "classification": f.classification,
                "matched_pattern": f.matched_pattern,  # Masked
                "action": f.action,
            }
            for f in findings
        ]

    @staticmethod
    async def search_security_policies(db: AsyncSession, policy_type: Optional[str] = None) -> List[Dict[str, Any]]:
        query = select(SecurityPolicy).where(SecurityPolicy.enabled == True)
        if policy_type:
            query = query.where(SecurityPolicy.policy_type == policy_type)
        res = await db.execute(query)
        policies = res.scalars().all()
        return [
            {"id": p.id, "name": p.name, "type": p.policy_type, "configuration": p.configuration}
            for p in policies
        ]
