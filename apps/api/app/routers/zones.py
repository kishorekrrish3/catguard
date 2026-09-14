from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List
from uuid import UUID
import json

from app.database import get_db
from app.models.zone import Zone
from app.models.alert import Alert, AlertStatus
from app.models.sensor import Sensor
from app.models.detection import Detection
from app.models.imagery import SatelliteImagery
from app.core.security import get_current_active_user, require_roles
from app.schemas.zone import ZoneCreate, ZoneUpdate, ZoneResponse, ZoneSummary
from app.schemas.common import PaginatedResponse
from geoalchemy2.shape import from_shape
from shapely.geometry import shape

router = APIRouter(prefix="/zones", tags=["Zones"])


@router.get("", response_model=PaginatedResponse[ZoneResponse])
async def list_zones(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    query = select(Zone)
    if status:
        query = query.where(Zone.status == status)
    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    result = await db.execute(query.offset((page - 1) * size).limit(size).order_by(Zone.name))
    zones = result.scalars().all()
    return PaginatedResponse(
        items=zones, total=total, page=page, size=size,
        pages=(total + size - 1) // size,
    )


@router.get("/{zone_id}", response_model=ZoneResponse)
async def get_zone(zone_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)):
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    return zone


@router.post("", response_model=ZoneResponse, status_code=201)
async def create_zone(
    data: ZoneCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("forest_manager", "administrator")),
):
    zone = Zone(name=data.name, description=data.description, status=data.status, area_hectares=data.area_hectares)
    if data.geojson:
        try:
            geom = shape(data.geojson)
            zone.geom = from_shape(geom, srid=4326)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid GeoJSON geometry")
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return zone


@router.put("/{zone_id}", response_model=ZoneResponse)
async def update_zone(
    zone_id: UUID,
    data: ZoneUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("forest_manager", "administrator")),
):
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(zone, field, value)
    await db.commit()
    await db.refresh(zone)
    return zone


@router.delete("/{zone_id}")
async def archive_zone(
    zone_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("administrator")),
):
    result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    zone.status = "archived"
    await db.commit()
    return {"message": "Zone archived"}


@router.get("/{zone_id}/summary", response_model=ZoneSummary)
async def get_zone_summary(zone_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)):
    zone_result = await db.execute(select(Zone).where(Zone.id == zone_id))
    zone = zone_result.scalar_one_or_none()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    active_alerts = await db.execute(
        select(func.count()).where(Alert.zone_id == zone_id, Alert.status == AlertStatus.active)
    )
    total_sensors = await db.execute(select(func.count()).where(Sensor.zone_id == zone_id))
    healthy_sensors = await db.execute(
        select(func.count()).where(Sensor.zone_id == zone_id, Sensor.is_active == True, Sensor.battery_level > 20)
    )
    recent_detections = await db.execute(select(func.count()).where(Detection.zone_id == zone_id))
    latest_imagery = await db.execute(
        select(SatelliteImagery).where(SatelliteImagery.zone_id == zone_id)
        .order_by(desc(SatelliteImagery.acquisition_date)).limit(1)
    )
    imagery = latest_imagery.scalar_one_or_none()

    return ZoneSummary(
        zone=zone,
        ndvi_mean=imagery.ndvi_mean if imagery else None,
        ndvi_trend=None,
        active_alerts=active_alerts.scalar(),
        total_sensors=total_sensors.scalar(),
        healthy_sensors=healthy_sensors.scalar(),
        recent_detections=recent_detections.scalar(),
    )
