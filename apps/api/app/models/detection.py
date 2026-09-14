import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.database import Base
import enum


class DetectionType(str, enum.Enum):
    illegal_logging = "illegal_logging"
    encroachment = "encroachment"
    fire_risk = "fire_risk"
    vegetation_loss = "vegetation_loss"
    suspicious_activity = "suspicious_activity"
    flood_risk = "flood_risk"


class DetectionSeverity(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class Detection(Base):
    __tablename__ = "detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False)
    detection_type = Column(SAEnum(DetectionType, name="detection_type_enum"), nullable=False)
    confidence = Column(Float, nullable=False)
    location = Column(Geometry("POINT", srid=4326), nullable=True)
    bounding_box = Column(Geometry("POLYGON", srid=4326), nullable=True)
    severity = Column(SAEnum(DetectionSeverity, name="detection_severity_enum"), nullable=False)
    model_version = Column(String(50), default="v1.0")
    image_url = Column(String(1024), nullable=True)
    verified = Column(Boolean, default=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    metadata_json = Column(JSONB, default={})

    zone = relationship("Zone", back_populates="detections")
    verifier = relationship("User", foreign_keys=[verified_by])
