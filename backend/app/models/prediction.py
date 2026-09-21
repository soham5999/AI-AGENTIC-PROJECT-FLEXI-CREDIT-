from sqlalchemy import Column, String, Float, DateTime, Text, ForeignKey
from datetime import datetime
from app.database import Base

class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, index=True)
    vehicle_id = Column(String, ForeignKey("vehicles.id"), nullable=True, index=True)
    risk_level = Column(String, nullable=False)          # LOW, MEDIUM, HIGH
    probability = Column(Float, nullable=False)          # 0.0 - 100.0
    maintenance_required = Column(String, nullable=False)# YES, NO
    affected_subsystems = Column(Text, nullable=True)    # JSON string
    input_features = Column(Text, nullable=True)         # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
