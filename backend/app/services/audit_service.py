from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog
from app.core.logging import logger


async def log_audit_event(
    db: AsyncSession,
    action: str,
    resource_type: str,
    resource_id: str,
    result: str,
    actor_id: Optional[str] = None,
    actor_email: str = "system",
    metadata: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    """
    Persists an immutable audit log record to the database.
    Scrubs any potential credential fields from metadata before storage.
    """
    clean_metadata = {}
    if metadata:
        for k, v in metadata.items():
            if any(term in k.lower() for term in ("password", "token", "secret", "authorization")):
                clean_metadata[k] = "[REDACTED]"
            else:
                clean_metadata[k] = v

    audit_entry = AuditLog(
        actor_id=actor_id,
        actor_email=actor_email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        result=result,
        metadata_payload=clean_metadata,
    )
    db.add(audit_entry)
    await db.commit()

    logger.info(
        f"AUDIT: [{result}] {actor_email} -> {action} on {resource_type}:{resource_id}",
        extra={"actor": actor_email, "action": action, "resource_id": resource_id},
    )
    return audit_entry
