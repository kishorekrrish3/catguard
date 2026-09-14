import uuid
import hashlib
import json
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    changes_json = Column(JSONB, default={})
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    integrity_hash = Column(String(64), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")

    @staticmethod
    def compute_hash(user_id: str, action: str, resource_type: str, resource_id: str, timestamp: str, changes: dict) -> str:
        payload = json.dumps({
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "timestamp": timestamp,
            "changes": changes,
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()
