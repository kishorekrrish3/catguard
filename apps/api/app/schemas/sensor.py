from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class SensorCreate(BaseModel):
    zone_id: UUID
    sensor_type: str
    name: str
    lat: float
    lng: float
    protocol: str = "lorawan"
    battery_level: Optional[float] = 100.0


class SensorResponse(BaseModel):
    id: UUID
    zone_id: UUID
    sensor_type: str
    name: str
    protocol: str
    battery_level: Optional[float]
    is_active: bool
    last_reading_at: Optional[datetime]
    last_value: Optional[float]
    installed_at: datetime

    model_config = {"from_attributes": True}


class SensorReadingResponse(BaseModel):
    id: UUID
    sensor_id: UUID
    timestamp: datetime
    value: float
    unit: Optional[str]
    quality_flag: str

    model_config = {"from_attributes": True}


class SensorHealth(BaseModel):
    total: int
    active: int
    offline: int
    low_battery: int
    by_type: dict
