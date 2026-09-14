from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    forest_manager = "forest_manager"
    field_officer = "field_officer"
    data_analyst = "data_analyst"
    community_reporter = "community_reporter"
    administrator = "administrator"


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: str
    full_name: Optional[str] = None
    password: str = Field(..., min_length=8)
    role: UserRole
    zone_id: Optional[UUID] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    zone_id: Optional[UUID] = None
    preferences: Optional[dict] = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: Optional[str]
    role: str
    zone_id: Optional[UUID]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
