import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid_str() -> str:
    return str(uuid.uuid4())


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    incident_id: Mapped[str] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("security_events.id", ondelete="CASCADE"), primary_key=True)


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_str)
    incident_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # LOW, MEDIUM, HIGH, CRITICAL
    status: Mapped[str] = mapped_column(String(30), default="OPEN", nullable=False, index=True)  # OPEN, INVESTIGATING, CONTAINED, RESOLVED, CLOSED
    risk_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 0 - 100
    risk_factors: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), default=1.000, nullable=False)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, onupdate=get_utc_now, nullable=False)

    events: Mapped[List["SecurityEvent"]] = relationship(
        "SecurityEvent",
        secondary="incident_events",
        back_populates="incidents",
        lazy="selectin",
    )
    investigation_reports: Mapped[List["InvestigationReport"]] = relationship(
        "InvestigationReport", back_populates="incident", cascade="all, delete-orphan", lazy="selectin"
    )
    remediation_actions: Mapped[List["RemediationAction"]] = relationship(
        "RemediationAction", back_populates="incident", cascade="all, delete-orphan", lazy="selectin"
    )


class InvestigationReport(Base):
    __tablename__ = "investigation_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_str)
    incident_id: Mapped[str] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    attack_chain: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    evidence: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    findings: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    recommendations: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    model_used: Mapped[str] = mapped_column(String(80), nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    incident: Mapped["Incident"] = relationship("Incident", back_populates="investigation_reports")


class RemediationAction(Base):
    __tablename__ = "remediation_actions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_str)
    incident_id: Mapped[str] = mapped_column(String(36), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    action_type: Mapped[str] = mapped_column(String(80), nullable=False)  # DISABLE_USER, REVOKE_TOKEN, ISOLATE_ASSET
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING_APPROVAL", nullable=False)  # PENDING_APPROVAL, APPROVED, REJECTED, EXECUTED, FAILED
    requested_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    executed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    incident: Mapped["Incident"] = relationship("Incident", back_populates="remediation_actions")
