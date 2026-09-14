import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class ImagerySource(str, enum.Enum):
    sentinel2 = "sentinel2"
    landsat9 = "landsat9"
    commercial = "commercial"
    drone = "drone"


class ProcessingStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class SatelliteImagery(Base):
    __tablename__ = "satellite_imagery"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False)
    acquisition_date = Column(Date, nullable=False)
    cloud_cover_percent = Column(Float, nullable=True)
    ndvi_mean = Column(Float, nullable=True)
    ndvi_min = Column(Float, nullable=True)
    ndvi_max = Column(Float, nullable=True)
    savi_mean = Column(Float, nullable=True)
    source = Column(SAEnum(ImagerySource, name="imagery_source_enum"), default=ImagerySource.sentinel2)
    path_url = Column(String(1024), nullable=True)
    thumbnail_url = Column(String(1024), nullable=True)
    processing_status = Column(SAEnum(ProcessingStatus, name="processing_status_enum"), default=ProcessingStatus.pending)
    metadata_json = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    zone = relationship("Zone", back_populates="imagery")
