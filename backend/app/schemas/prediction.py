from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PredictionInput(BaseModel):
    vehicle_age: float = Field(..., ge=0, le=50, example=3.0)
    odometer_km: float = Field(..., ge=0, example=62450)
    days_since_service: float = Field(..., ge=0, example=195)
    battery_voltage: float = Field(..., ge=8.0, le=16.0, example=11.9)
    engine_temp: float = Field(..., ge=40.0, le=150.0, example=99.0)
    brake_wear_pct: float = Field(..., ge=0.0, le=100.0, example=78.0)
    tire_pressure_avg: float = Field(..., ge=15.0, le=50.0, example=30.0)
    oil_life_pct: float = Field(..., ge=0.0, le=100.0, example=22.0)
    vehicle_id: Optional[str] = Field(None, example="v-camry-01")

class AffectedSubsystem(BaseModel):
    name: str
    severity: str # Critical, Moderate, Low
    detail: str

class PredictionOut(BaseModel):
    id: str
    timestamp: str
    probability: float
    riskLevel: str              # HIGH, MEDIUM, LOW
    maintenanceRequired: str    # YES, NO
    affectedAreas: List[AffectedSubsystem]
    featureImportances: Optional[List[Dict[str, Any]]] = None
    inputs: Dict[str, Any]
    model_version: str = "RandomForest-v2.4"
