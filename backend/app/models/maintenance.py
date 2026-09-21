from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(String, primary_key=True, index=True)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=False, index=True)
    date = Column(String, nullable=False)
    mileage = Column(Integer, nullable=False)
    service_type = Column(String, nullable=False)
    cost = Column(Float, nullable=False, default=0.0)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
