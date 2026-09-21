from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MaintenanceCreate(BaseModel):
    vehicle_id: str = Field(..., example="v-camry-01")
    date: str = Field(..., example="2026-03-15")
    mileage: int = Field(..., ge=0, example=62500)
    service_type: str = Field(..., example="Synthetic Oil & Filter Change")
    cost: float = Field(0.0, ge=0.0, example=120.0)
    notes: Optional[str] = Field(None, example="Replaced full synthetic 0W-20")

class MaintenanceOut(MaintenanceCreate):
    id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
