from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class VehicleBase(BaseModel):
    make: str = Field(..., example="Toyota")
    model: str = Field(..., example="Camry Hybrid")
    year: int = Field(..., ge=1990, le=2030, example=2021)
    type: str = Field("Sedan", example="Sedan")
    mileage: int = Field(..., ge=0, example=62450)
    days_since_service: int = Field(..., ge=0, example=195)
    battery_voltage: float = Field(..., ge=8.0, le=16.0, example=11.9)
    engine_temp: float = Field(..., ge=40.0, le=150.0, example=99.0)
    brake_wear_pct: float = Field(..., ge=0.0, le=100.0, example=78.0)
    tire_pressure_avg: float = Field(..., ge=15.0, le=50.0, example=30.0)
    oil_life_pct: float = Field(..., ge=0.0, le=100.0, example=22.0)

class VehicleCreate(VehicleBase):
    id: Optional[str] = None

class VehicleUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    type: Optional[str] = None
    mileage: Optional[int] = None
    days_since_service: Optional[int] = None
    battery_voltage: Optional[float] = None
    engine_temp: Optional[float] = None
    brake_wear_pct: Optional[float] = None
    tire_pressure_avg: Optional[float] = None
    oil_life_pct: Optional[float] = None

class VehicleOut(VehicleBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
