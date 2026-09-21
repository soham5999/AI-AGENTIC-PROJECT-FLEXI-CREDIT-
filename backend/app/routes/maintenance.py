from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.maintenance import MaintenanceRecord
from app.schemas.maintenance import MaintenanceCreate, MaintenanceOut

router = APIRouter(prefix="/maintenance", tags=["Maintenance Records"])

@router.get("/{vehicle_id}", response_model=List[MaintenanceOut])
def get_vehicle_maintenance_records(vehicle_id: str, db: Session = Depends(get_db)):
    """Retrieve all service and repair records for a specific vehicle."""
    records = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.vehicle_id == vehicle_id
    ).order_by(MaintenanceRecord.date.desc()).all()
    return records

@router.post("", response_model=MaintenanceOut, status_code=status.HTTP_201_CREATED)
def add_maintenance_record(payload: MaintenanceCreate, db: Session = Depends(get_db)):
    """Add a new service record into SQLite database."""
    record_id = f"m-{int(datetime.utcnow().timestamp() * 1000)}"
    rec = MaintenanceRecord(
        id=record_id,
        vehicle_id=payload.vehicle_id,
        date=payload.date,
        mileage=payload.mileage,
        service_type=payload.service_type,
        cost=payload.cost,
        notes=payload.notes,
        created_at=datetime.utcnow()
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@router.delete("/{record_id}")
def delete_maintenance_record(record_id: str, db: Session = Depends(get_db)):
    """Delete a maintenance log entry."""
    rec = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    db.delete(rec)
    db.commit()
    return {"status": "deleted", "id": record_id}
