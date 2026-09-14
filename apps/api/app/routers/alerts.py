from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, update
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.alert import Alert, AlertStatus, AlertSeverity
from app.models.alert_rule import AlertRule
from app.core.security import get_current_active_user, require_roles
from app.core.redis_client import publish_alert
from app.schemas.alert import AlertResponse, AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse, AlertAcknowledge, AlertStats
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=PaginatedResponse[AlertResponse])
async def list_alerts(
    zone_id: Optional[UUID] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    query = select(Alert)
    if zone_id:
        query = query.where(Alert.zone_id == zone_id)
    if severity:
        query = query.where(Alert.severity == severity)
    if status:
        query = query.where(Alert.status == status)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    result = await db.execute(query.order_by(desc(Alert.created_at)).offset((page - 1) * size).limit(size))
    return PaginatedResponse(items=result.scalars().all(), total=total, page=page, size=size, pages=(total + size - 1) // size)


@router.get("/stats", response_model=AlertStats)
async def get_alert_stats(zone_id: Optional[UUID] = None, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)):
    query = select(Alert)
    if zone_id:
        query = query.where(Alert.zone_id == zone_id)
    result = await db.execute(query)
    alerts = result.scalars().all()
    by_severity: dict = {}
    by_status: dict = {}
    by_type: dict = {}
    for a in alerts:
        by_severity[a.severity.value] = by_severity.get(a.severity.value, 0) + 1
        by_status[a.status.value] = by_status.get(a.status.value, 0) + 1
        by_type[a.alert_type.value] = by_type.get(a.alert_type.value, 0) + 1
    return AlertStats(total=len(alerts), by_severity=by_severity, by_status=by_status, by_type=by_type)


@router.get("/rules", response_model=List[AlertRuleResponse])
async def list_alert_rules(zone_id: Optional[UUID] = None, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)):
    query = select(AlertRule)
    if zone_id:
        query = query.where(AlertRule.zone_id == zone_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/rules", response_model=AlertRuleResponse, status_code=201)
async def create_alert_rule(
    data: AlertRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("forest_manager", "administrator")),
):
    rule = AlertRule(**data.model_dump(), created_by=current_user.id)
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: UUID,
    data: AlertRuleUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("forest_manager", "administrator")),
):
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(rule, field, value)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/rules/{rule_id}")
async def delete_alert_rule(
    rule_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("forest_manager", "administrator")),
):
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    await db.delete(rule)
    await db.commit()
    return {"message": "Alert rule deleted"}


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: UUID,
    body: AlertAcknowledge,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = AlertStatus.acknowledged
    alert.acknowledged_by = current_user.id
    alert.acknowledged_at = datetime.utcnow()
    await db.commit()
    await publish_alert({"event": "alert_acknowledged", "alert_id": str(alert_id), "user": current_user.username})
    return {"message": "Alert acknowledged"}


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = AlertStatus.resolved
    alert.resolved_at = datetime.utcnow()
    await db.commit()
    return {"message": "Alert resolved"}


@router.post("/{alert_id}/false-positive")
async def mark_false_positive(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("forest_manager", "data_analyst", "administrator")),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = AlertStatus.false_positive
    await db.commit()
    return {"message": "Alert marked as false positive"}
