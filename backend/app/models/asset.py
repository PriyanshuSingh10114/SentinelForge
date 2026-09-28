import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid_str() -> str:
    return str(uuid.uuid4())


class DataClassification(Base):
    __tablename__ = "data_classifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_str)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity_weight: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    assets: Mapped[List["Asset"]] = relationship("Asset", back_populates="classification")


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_str)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # DATABASE, BUCKET, API, SERVER, REPOSITORY
    environment: Mapped[str] = mapped_column(String(50), default="production", nullable=False)
    owner: Mapped[str] = mapped_column(String(100), nullable=False)
    classification_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("data_classifications.id"), nullable=True)
    asset_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_utc_now, nullable=False)

    classification: Mapped[Optional["DataClassification"]] = relationship(
        "DataClassification", back_populates="assets", lazy="selectin"
    )
