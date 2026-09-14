from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class DetectionResponse(BaseModel):
    id: UUID
    zone_id: UUID
    detection_type: str
    confidence: float
    severity: str
    location: Optional[dict] = None
    image_url: Optional[str]
    verified: bool
    notes: Optional[str]
    timestamp: datetime
    model_version: str

    model_config = {"from_attributes": True}


class DetectionFeedback(BaseModel):
    detection_id: UUID
    verified: bool
    notes: Optional[str] = None


class DetectionAccuracy(BaseModel):
    zone_id: Optional[UUID]
    total_detections: int
    verified_count: int
    false_positive_count: int
    precision: Optional[float]
    recall: Optional[float]
    f1_score: Optional[float]
    by_type: List[dict]


class DetectionTimelinePoint(BaseModel):
    date: str
    count: int
    by_type: dict
