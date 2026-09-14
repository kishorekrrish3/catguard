from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any, Generic, TypeVar
from uuid import UUID
from datetime import datetime
from enum import Enum

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None


class SuccessResponse(BaseModel):
    message: str
    data: Optional[Any] = None
