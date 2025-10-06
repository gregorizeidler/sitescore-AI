from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .base import Base

class OverpassAudit(Base):
    __tablename__ = "overpass_audit"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    query_hash = Column(String, index=True, nullable=False)
    bbox = Column(String, nullable=True)
    status = Column(String, default="success")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
