from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from app.database import Base

class DatasetRecord(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    records = Column(Integer, nullable=False, default=0)
    features = Column(Integer, nullable=False, default=0)
    target_column = Column(String, nullable=False, default="maintenance_required")
    status = Column(String, nullable=False, default="active") # active, archived
    uploaded_at = Column(DateTime, default=datetime.utcnow)
