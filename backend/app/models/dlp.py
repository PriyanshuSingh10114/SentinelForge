import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid_str() -> str:
    return str(uuid.uuid4())


class DlpFinding(Base):
    __tablename__ = "dlp_findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_str)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # PAYLOAD, FILE_UPLOAD, GIT_COMMIT
    source_id: Mapped[str] = mapped_column(String(120), nullable=False)
    data_type: Mapped[str] = mapped_column(String(60), nullable=False, index=True)  # AWS_KEY, JWT, PII_EMAIL
    classification: Mapped[str] = mapped_column(String(30), nullable=False)  # PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED
    matched_pattern: Mapped[str] = mapped_column(String(255), nullable=False)  # ALWAYS MASKED: AKIA****************MPLE
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False)  # ALLOW, WARN, BLOCK, QUARANTINE
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)


class SecurityPolicy(Base):
    __tablename__ = "security_policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_str)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    policy_type: Mapped[str] = mapped_column(String(50), nullable=False)  # DLP, RATE_LIMIT, ACCESS_CONTROL
    configuration: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)
