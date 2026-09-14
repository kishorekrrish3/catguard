from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date


class ImageryCreate(BaseModel):
    zone_id: UUID
    acquisition_date: date
    cloud_cover_percent: Optional[float] = None
    source: str = "sentinel2"


class ImageryProcessRequest(BaseModel):
    imagery_id: UUID


class ImageryResponse(BaseModel):
    id: UUID
    zone_id: UUID
    acquisition_date: date
    cloud_cover_percent: Optional[float]
    ndvi_mean: Optional[float]
    ndvi_min: Optional[float]
    ndvi_max: Optional[float]
    savi_mean: Optional[float]
    source: str
    path_url: Optional[str]
    thumbnail_url: Optional[str]
    processing_status: str
    created_at: datetime

    model_config = {"from_attributes": True}
