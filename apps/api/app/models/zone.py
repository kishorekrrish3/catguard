import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Text, Float, Boolean, DateTime, Date,
    ForeignKey, Integer, Enum as SAEnum, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.database import Base
import enum


class ZoneStatus(str, enum.Enum):
    active = "active"
    monitoring = "monitoring"
    restricted = "restricted"
    archived = "archived"


class Zone(Base):
    __tablename__ = "zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    geom = Column(Geometry("POLYGON", srid=4326), nullable=True)
    status = Column(SAEnum(ZoneStatus, name="zone_status_enum"), default=ZoneStatus.active, nullable=False)
    area_hectares = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    sensors = relationship("Sensor", back_populates="zone", lazy="select")
    detections = relationship("Detection", back_populates="zone", lazy="select")
    imagery = relationship("SatelliteImagery", back_populates="zone", lazy="select")
    alerts = relationship("Alert", back_populates="zone", lazy="select")
    community_reports = relationship("CommunityReport", back_populates="zone", lazy="select")
