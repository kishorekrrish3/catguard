from pydantic import BaseModel, Field
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime


class ZoneCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    status: str = "active"
    area_hectares: Optional[float] = None
    geojson: Optional[dict] = None  # GeoJSON polygon geometry


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    area_hectares: Optional[float] = None


class ZoneResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    status: str
    area_hectares: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class ZoneSummary(BaseModel):
    zone: ZoneResponse
    ndvi_mean: Optional[float]
    ndvi_trend: Optional[float]
    active_alerts: int
    total_sensors: int
    healthy_sensors: int
    recent_detections: int
