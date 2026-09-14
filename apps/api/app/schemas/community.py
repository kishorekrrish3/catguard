from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CommunityReportCreate(BaseModel):
    zone_id: Optional[UUID] = None
    report_type: str
    description: str = Field(..., min_length=10)
    lat: float
    lng: float
    is_anonymous: bool = False
    photo_urls: List[str] = []


class CommunityReportResponse(BaseModel):
    id: UUID
    zone_id: Optional[UUID]
    report_type: str
    description: str
    status: str
    is_anonymous: bool
    photo_urls: List[str]
    submitted_at: datetime
    updated_at: Optional[datetime]
    resolution_notes: Optional[str]

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: UUID
    username: str
    full_name: Optional[str]
    total_reports: int
    verified_reports: int
    score: float
