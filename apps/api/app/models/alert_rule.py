import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Float, Integer, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class RuleOperator(str, enum.Enum):
    gt = "gt"
    lt = "lt"
    gte = "gte"
    lte = "lte"
    eq = "eq"
    neq = "neq"


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(UUID(as_uuid=True), ForeignKey("zones.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    alert_type = Column(String(100), nullable=False)
    condition_field = Column(String(100), nullable=False)
    condition_operator = Column(SAEnum(RuleOperator, name="rule_operator_enum"), nullable=False)
    condition_value = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False, default="medium")
    is_active = Column(Boolean, default=True)
    cooldown_minutes = Column(Integer, default=60)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    zone = relationship("Zone", foreign_keys=[zone_id])
    creator = relationship("User", foreign_keys=[created_by])
