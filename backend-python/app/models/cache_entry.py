from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from .base import Base

class CacheEntry(Base):
    __tablename__ = "overpass_cache"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, index=True, unique=True, nullable=False)
    geom = Column(Geometry(geometry_type="GEOMETRY", srid=4326, spatial_index=True), nullable=False)
    payload = Column(JSON, nullable=False)
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
