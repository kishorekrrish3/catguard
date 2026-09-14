from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class AlertResponse(BaseModel):
    id: UUID
    zone_id: UUID
    alert_type: str
    severity: str
    title: str
    description: Optional[str]
    status: str
    source_type: str
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    zone_id: Optional[UUID] = None
    alert_type: str
    condition_field: str
    condition_operator: str
    condition_value: float
    severity: str = "medium"
    cooldown_minutes: int = 60


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    condition_value: Optional[float] = None
    severity: Optional[str] = None
    is_active: Optional[bool] = None
    cooldown_minutes: Optional[int] = None


class AlertRuleResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    zone_id: Optional[UUID]
    alert_type: str
    condition_field: str
    condition_operator: str
    condition_value: float
    severity: str
    is_active: bool
    cooldown_minutes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertAcknowledge(BaseModel):
    notes: Optional[str] = None


class AlertStats(BaseModel):
    total: int
    by_severity: dict
    by_status: dict
    by_type: dict
