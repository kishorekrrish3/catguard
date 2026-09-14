from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

from app.database import get_db
from app.models.sensor import Sensor
from app.models.sensor_reading import SensorReading
from app.core.security import get_current_active_user, require_roles
from app.schemas.sensor import SensorCreate, SensorResponse, SensorReadingResponse, SensorHealth
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/sensors", tags=["Sensors"])


@router.get("/list", response_model=PaginatedResponse[SensorResponse])
async def list_sensors(
    zone_id: Optional[UUID] = None,
    sensor_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    query = select(Sensor)
    if zone_id:
        query = query.where(Sensor.zone_id == zone_id)
    if sensor_type:
        query = query.where(Sensor.sensor_type == sensor_type)
    if is_active is not None:
        query = query.where(Sensor.is_active == is_active)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    result = await db.execute(query.offset((page - 1) * size).limit(size))
    return PaginatedResponse(items=result.scalars().all(), total=total, page=page, size=size, pages=(total + size - 1) // size)


@router.get("/health", response_model=SensorHealth)
async def get_sensor_health(zone_id: Optional[UUID] = None, db: AsyncSession = Depends(get_db), _=Depends(get_current_active_user)):
    query = select(Sensor)
    if zone_id:
        query = query.where(Sensor.zone_id == zone_id)
    result = await db.execute(query)
    sensors = result.scalars().all()
    by_type: dict = {}
    low_battery = 0
    offline = 0
    for s in sensors:
        by_type[s.sensor_type.value] = by_type.get(s.sensor_type.value, 0) + 1
        if s.battery_level is not None and s.battery_level < 20:
            low_battery += 1
        if not s.is_active:
            offline += 1
    return SensorHealth(total=len(sensors), active=len(sensors) - offline, offline=offline, low_battery=low_battery, by_type=by_type)


@router.get("/{sensor_id}/readings", response_model=List[SensorReadingResponse])
async def get_sensor_readings(
    sensor_id: UUID,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = Query(288, ge=1, le=2000),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_active_user),
):
    if not start:
        start = datetime.utcnow() - timedelta(days=7)
    if not end:
        end = datetime.utcnow()
    result = await db.execute(
        select(SensorReading)
        .where(SensorReading.sensor_id == sensor_id, SensorReading.timestamp >= start, SensorReading.timestamp <= end)
        .order_by(SensorReading.timestamp)
        .limit(limit)
    )
    return result.scalars().all()


@router.post("/{sensor_id}/calibrate")
async def calibrate_sensor(
    sensor_id: UUID,
    offset: float = Query(..., description="Calibration offset value"),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("forest_manager", "field_officer", "administrator")),
):
    result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    sensor.calibration_offset = offset
    await db.commit()
    return {"message": "Calibration updated", "sensor_id": str(sensor_id), "offset": offset}


@router.post("", response_model=SensorResponse, status_code=201)
async def create_sensor(
    data: SensorCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("forest_manager", "administrator")),
):
    sensor = Sensor(
        zone_id=data.zone_id,
        sensor_type=data.sensor_type,
        name=data.name,
        location=from_shape(Point(data.lng, data.lat), srid=4326),
        protocol=data.protocol,
        battery_level=data.battery_level,
    )
    db.add(sensor)
    await db.commit()
    await db.refresh(sensor)
    return sensor


@router.delete("/{sensor_id}")
async def decommission_sensor(
    sensor_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_roles("forest_manager", "administrator")),
):
    result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    sensor.is_active = False
    await db.commit()
    return {"message": "Sensor decommissioned"}
