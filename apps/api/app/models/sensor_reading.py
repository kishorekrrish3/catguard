import uuid
from datetime import datetime
from sqlalchemy import Column, Float, DateTime, ForeignKey, String, Enum as SAEnum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class QualityFlag(str, enum.Enum):
    good = "good"
    suspect = "suspect"
    bad = "bad"


class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), primary_key=True, nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    quality_flag = Column(SAEnum(QualityFlag, name="quality_flag_enum"), default=QualityFlag.good)
    raw_value = Column(Float, nullable=True)
    metadata_json = Column(JSONB, default={})

    sensor = relationship("Sensor", back_populates="readings")

    __table_args__ = (
        Index("ix_sensor_readings_sensor_timestamp", "sensor_id", "timestamp"),
    )
