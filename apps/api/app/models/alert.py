import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SAEnum, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.database import Base
import enum


class AlertType(str, enum.Enum):
    vegetation_loss = "vegetation_loss"
    illegal_activity = "illegal_activity"
    sensor_anomaly = "sensor_anomaly"
    unauthorized_access = "unauthorized_access"
    fire_risk = "fire_risk"
    weather_extreme = "weather_extreme"


class AlertSeverity(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class AlertStatus(str, enum.Enum):
    active = "active"
    acknowledged = "acknowledged"
    resolved = "resolved"
    false_positive = "false_positive"


class AlertSource(str, enum.Enum):
    ml_detection = "ml_detection"
    sensor_threshold = "sensor_threshold"
    community_report = "community_report"
    manual = "manual"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False)
    alert_type = Column(SAEnum(AlertType, name="alert_type_enum"), nullable=False)
    severity = Column(SAEnum(AlertSeverity, name="alert_severity_enum"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SAEnum(AlertStatus, name="alert_status_enum"), default=AlertStatus.active)
    source_type = Column(SAEnum(AlertSource, name="alert_source_enum"), default=AlertSource.ml_detection)
    source_id = Column(UUID(as_uuid=True), nullable=True)
    location = Column(Geometry("POINT", srid=4326), nullable=True)
    acknowledged_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    metadata_json = Column(JSONB, default={})

    zone = relationship("Zone", back_populates="alerts")
    acknowledger = relationship("User", foreign_keys=[acknowledged_by])
