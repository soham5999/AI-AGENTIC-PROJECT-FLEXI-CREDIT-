from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleOut

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

@router.get("", response_model=List[VehicleOut])
def list_vehicles(db: Session = Depends(get_db)):
    """Retrieve all vehicles stored in SQLite."""
    return db.query(Vehicle).all()

@router.get("/default/demo", response_model=VehicleOut)
def get_default_vehicle(db: Session = Depends(get_db)):
    """Retrieve the primary demo fleet vehicle."""
    v = db.query(Vehicle).first()
    if not v:
        # Create default demo vehicle
        v = Vehicle(
            id="v-camry-01",
            make="Toyota",
            model="Camry Hybrid (Demo Fleet Vehicle)",
            year=2021,
            type="Sedan",
            mileage=62450,
            days_since_service=195,
            battery_voltage=11.9,
            engine_temp=99.0,
            brake_wear_pct=78.0,
            tire_pressure_avg=30.0,
            oil_life_pct=22.0
        )
        db.add(v)
        db.commit()
        db.refresh(v)
    return v

@router.get("/{vehicle_id}", response_model=VehicleOut)
def get_vehicle_by_id(vehicle_id: str, db: Session = Depends(get_db)):
    """Retrieve a specific vehicle by ID."""
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return v

@router.post("", response_model=VehicleOut, status_code=status.HTTP_201_CREATED)
def create_vehicle(payload: VehicleCreate, db: Session = Depends(get_db)):
    """Register a new vehicle with telemetry baselines."""
    vid = payload.id or f"v-{int(datetime.utcnow().timestamp())}"
    existing = db.query(Vehicle).filter(Vehicle.id == vid).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle with this ID already exists")

    new_v = Vehicle(
        id=vid,
        make=payload.make,
        model=payload.model,
        year=payload.year,
        type=payload.type,
        mileage=payload.mileage,
        days_since_service=payload.days_since_service,
        battery_voltage=payload.battery_voltage,
        engine_temp=payload.engine_temp,
        brake_wear_pct=payload.brake_wear_pct,
        tire_pressure_avg=payload.tire_pressure_avg,
        oil_life_pct=payload.oil_life_pct
    )
    db.add(new_v)
    db.commit()
    db.refresh(new_v)
    return new_v

@router.put("/{vehicle_id}", response_model=VehicleOut)
def update_vehicle(vehicle_id: str, payload: VehicleUpdate, db: Session = Depends(get_db)):
    """Update telemetry parameters for a vehicle."""
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    update_data = payload.dict(exclude_unset=True)
    for key, value in update_data.items():
        if value is not None:
            setattr(v, key, value)

    v.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(v)
    return v
