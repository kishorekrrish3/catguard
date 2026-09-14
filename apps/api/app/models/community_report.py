import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.database import Base
import enum


class ReportType(str, enum.Enum):
    illegal_logging = "illegal_logging"
    encroachment = "encroachment"
    fire = "fire"
    poaching = "poaching"
    waste_dumping = "waste_dumping"
    other = "other"


class ReportStatus(str, enum.Enum):
    pending = "pending"
    under_review = "under_review"
    verified = "verified"
    resolved = "resolved"
    rejected = "rejected"


class CommunityReport(Base):
    __tablename__ = "community_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id", ondelete="SET NULL"), nullable=True)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_anonymous = Column(Boolean, default=False)
    report_type = Column(SAEnum(ReportType, name="report_type_enum"), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(Geometry("POINT", srid=4326), nullable=False)
    photo_urls = Column(JSONB, default=[])
    audio_url = Column(String(1024), nullable=True)
    status = Column(SAEnum(ReportStatus, name="report_status_enum"), default=ReportStatus.pending)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    zone = relationship("Zone", back_populates="community_reports")
    reporter = relationship("User", foreign_keys=[reporter_id])
    assignee = relationship("User", foreign_keys=[assigned_to])
    verifier = relationship("User", foreign_keys=[verified_by])
