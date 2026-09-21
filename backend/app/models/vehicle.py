from sqlalchemy import Column, String, Integer, Float, DateTime
from datetime import datetime
from app.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(String, primary_key=True, index=True)
    make = Column(String, nullable=False, default="Toyota")
    model = Column(String, nullable=False, default="Camry Hybrid")
    year = Column(Integer, nullable=False, default=2021)
    type = Column(String, nullable=False, default="Sedan")
    mileage = Column(Integer, nullable=False, default=62450)
    days_since_service = Column(Integer, nullable=False, default=195)
    battery_voltage = Column(Float, nullable=False, default=11.9)
    engine_temp = Column(Float, nullable=False, default=99.0)
    brake_wear_pct = Column(Float, nullable=False, default=78.0)
    tire_pressure_avg = Column(Float, nullable=False, default=30.0)
    oil_life_pct = Column(Float, nullable=False, default=22.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
