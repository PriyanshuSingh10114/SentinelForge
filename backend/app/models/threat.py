import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid_str() -> str:
    return str(uuid.uuid4())


class ThreatModel(Base):
    __tablename__ = "threat_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_str)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    architecture_summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    items: Mapped[List["ThreatModelItem"]] = relationship(
        "ThreatModelItem", back_populates="threat_model", cascade="all, delete-orphan", lazy="selectin"
    )


class ThreatModelItem(Base):
    __tablename__ = "threat_model_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_str)
    threat_model_id: Mapped[str] = mapped_column(String(36), ForeignKey("threat_models.id", ondelete="CASCADE"), nullable=False)
    stride_category: Mapped[str] = mapped_column(String(40), nullable=False)  # SPOOFING, TAMPERING, etc.
    target_component: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    mitigation: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="OPEN", nullable=False)  # OPEN, MITIGATED, ACCEPTED, FALSE_POSITIVE

    threat_model: Mapped["ThreatModel"] = relationship("ThreatModel", back_populates="items")
