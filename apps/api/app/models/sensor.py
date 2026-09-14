import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.database import Base
import enum


class SensorType(str, enum.Enum):
    soil_moisture = "soil_moisture"
    soil_temperature = "soil_temperature"
    soil_ph = "soil_ph"
    air_temperature = "air_temperature"
    humidity = "humidity"
    precipitation = "precipitation"
    motion = "motion"
    camera = "camera"
    air_quality = "air_quality"


class SensorProtocol(str, enum.Enum):
    lorawan = "lorawan"
    nb_iot = "nb_iot"
    wifi = "wifi"
    cellular = "cellular"


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False)
    sensor_type = Column(SAEnum(SensorType, name="sensor_type_enum"), nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(Geometry("POINT", srid=4326), nullable=False)
    protocol = Column(SAEnum(SensorProtocol, name="sensor_protocol_enum"), default=SensorProtocol.lorawan)
    battery_level = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    last_reading_at = Column(DateTime(timezone=True), nullable=True)
    last_value = Column(Float, nullable=True)
    calibration_offset = Column(Float, default=0.0)
    installed_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    metadata_json = Column(JSONB, default={})

    zone = relationship("Zone", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor", lazy="select")
