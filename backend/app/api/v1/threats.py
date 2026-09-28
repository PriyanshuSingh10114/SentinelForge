from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import NotFoundException
from app.database.session import get_db
from app.models.auth import User
from app.models.threat import ThreatModel, ThreatModelItem
from app.schemas.threat import (
    ThreatItemResponse,
    ThreatItemStatusUpdateRequest,
    ThreatModelCreateRequest,
    ThreatModelResponse,
)
from app.security.dependencies import get_current_user
from app.services.audit_service import log_audit_event
from app.threat_modeling.engine import analyze_architecture_and_generate_threats

router = APIRouter(prefix="/threat-models", tags=["STRIDE Threat Modeling"])


@router.post("", response_model=ThreatModelResponse, status_code=status.HTTP_201_CREATED)
async def create_threat_model(
    payload: ThreatModelCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a STRIDE threat model from architecture description.
    Maps trust boundaries, entry points, and components to STRIDE threats and mitigations.
    """
    model = ThreatModel(
        name=payload.name,
        architecture_summary=payload.architecture_summary,
        created_by=current_user.id,
    )
    db.add(model)
    await db.flush()

    generated_threats = analyze_architecture_and_generate_threats(payload.architecture_summary)
    for gt in generated_threats:
        item = ThreatModelItem(
            threat_model_id=model.id,
            stride_category=gt.stride_category,
            target_component=gt.target_component,
            description=gt.description,
            mitigation=gt.mitigation,
            status="OPEN",
        )
        db.add(item)

    await db.commit()
    await db.refresh(model)

    # Re-fetch with items loaded
    stmt = select(ThreatModel).options(selectinload(ThreatModel.items)).where(ThreatModel.id == model.id)
    res = await db.execute(stmt)
    saved_model = res.scalar_one()

    await log_audit_event(
        db=db,
        action="THREAT_MODEL_CREATED",
        resource_type="THREAT_MODEL",
        resource_id=model.id,
        result="SUCCESS",
        actor_id=current_user.id,
        actor_email=current_user.email,
        metadata={"name": model.name, "threats_count": len(generated_threats)},
    )

    return saved_model


@router.get("", response_model=List[ThreatModelResponse])
async def list_threat_models(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all STRIDE threat models.
    """
    stmt = select(ThreatModel).options(selectinload(ThreatModel.items)).order_by(ThreatModel.created_at.desc())
    res = await db.execute(stmt)
    models = res.scalars().all()
    return models


@router.get("/{model_id}", response_model=ThreatModelResponse)
async def get_threat_model(
    model_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve single STRIDE threat model with all threat items and mitigations.
    """
    stmt = select(ThreatModel).options(selectinload(ThreatModel.items)).where(ThreatModel.id == model_id)
    res = await db.execute(stmt)
    model = res.scalar_one_or_none()
    if not model:
        raise NotFoundException("ThreatModel", model_id)
    return model


@router.patch("/items/{item_id}/status", response_model=ThreatItemResponse)
async def update_threat_item_status(
    item_id: str,
    payload: ThreatItemStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update threat status (OPEN, MITIGATED, ACCEPTED, FALSE_POSITIVE).
    """
    stmt = select(ThreatModelItem).where(ThreatModelItem.id == item_id)
    res = await db.execute(stmt)
    item = res.scalar_one_or_none()
    if not item:
        raise NotFoundException("ThreatModelItem", item_id)

    old_status = item.status
    item.status = payload.status.upper()
    await db.commit()
    await db.refresh(item)

    await log_audit_event(
        db=db,
        action="THREAT_STATUS_UPDATED",
        resource_type="THREAT_MODEL_ITEM",
        resource_id=item.id,
        result="SUCCESS",
        actor_id=current_user.id,
        actor_email=current_user.email,
        metadata={"old_status": old_status, "new_status": item.status},
    )

    return item
