import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.ml.predictor import predict_maintenance, calculate_subsystem_health
from app.models.vehicle import Vehicle
from app.models.maintenance import MaintenanceRecord
from app.models.prediction import PredictionRecord
from app.config import settings

def get_vehicle_information_tool(vehicle_id: str, db: Session) -> Dict[str, Any]:
    """
    Tool 5: get_vehicle_information
    Retrieves stored vehicle telemetry and specification from the SQLite database.
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        # Fallback to default demo record if not found
        return {
            "status": "default_fallback",
            "id": "v-camry-01",
            "make": "Toyota",
            "model": "Camry Hybrid",
            "year": 2021,
            "type": "Sedan",
            "mileage": 62450,
            "days_since_service": 195,
            "battery_voltage": 11.9,
            "engine_temp": 99.0,
            "brake_wear_pct": 78.0,
            "tire_pressure_avg": 30.0,
            "oil_life_pct": 22.0
        }
    return {
        "status": "found",
        "id": vehicle.id,
        "make": vehicle.make,
        "model": vehicle.model,
        "year": vehicle.year,
        "type": vehicle.type,
        "mileage": vehicle.mileage,
        "days_since_service": vehicle.days_since_service,
        "battery_voltage": vehicle.battery_voltage,
        "engine_temp": vehicle.engine_temp,
        "brake_wear_pct": vehicle.brake_wear_pct,
        "tire_pressure_avg": vehicle.tire_pressure_avg,
        "oil_life_pct": vehicle.oil_life_pct
    }

def predict_vehicle_maintenance_tool(vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool 1: predict_vehicle_maintenance
    Invokes the trained Scikit-Learn Random Forest Classifier on vehicle telemetry.
    """
    # Calculate vehicle age
    curr_year = datetime.now().year
    year = vehicle_data.get("year", curr_year - 3)
    vehicle_age = float(curr_year - year) if year else 3.0

    features = {
        "vehicle_age": vehicle_age,
        "odometer_km": float(vehicle_data.get("mileage", 62450)),
        "days_since_service": float(vehicle_data.get("days_since_service", 195)),
        "battery_voltage": float(vehicle_data.get("battery_voltage", 11.9)),
        "engine_temp": float(vehicle_data.get("engine_temp", 99.0)),
        "brake_wear_pct": float(vehicle_data.get("brake_wear_pct", 78.0)),
        "tire_pressure_avg": float(vehicle_data.get("tire_pressure_avg", 30.0)),
        "oil_life_pct": float(vehicle_data.get("oil_life_pct", 22.0))
    }

    result = predict_maintenance(features)
    return result

def analyze_vehicle_health_tool(vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool 2: analyze_vehicle_health
    Evaluates specific mechanical subsystems against automotive safety thresholds.
    """
    subsystems = calculate_subsystem_health(vehicle_data)
    critical_count = sum(1 for s in subsystems if s.get("severity") == "Critical")
    moderate_count = sum(1 for s in subsystems if s.get("severity") == "Moderate")

    return {
        "total_anomalies": len(subsystems),
        "critical_count": critical_count,
        "moderate_count": moderate_count,
        "affected_subsystems": subsystems
    }

def get_maintenance_history_tool(vehicle_id: str, db: Session) -> Dict[str, Any]:
    """
    Tool 3: get_maintenance_history
    Retrieves previous maintenance records and calculates elapsed service intervals.
    """
    records = db.query(MaintenanceRecord).filter(
        MaintenanceRecord.vehicle_id == vehicle_id
    ).order_by(MaintenanceRecord.date.desc()).all()

    formatted_records = [
        {
            "id": r.id,
            "date": r.date,
            "mileage": r.mileage,
            "service_type": r.service_type,
            "cost": r.cost,
            "notes": r.notes
        }
        for r in records
    ]

    total_cost = sum(r.cost for r in records)
    last_service_date = formatted_records[0]["date"] if formatted_records else "None"

    return {
        "record_count": len(formatted_records),
        "total_spent_usd": total_cost,
        "last_service_date": last_service_date,
        "records": formatted_records[:5]
    }

def save_prediction_tool(vehicle_id: str, prediction_data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Tool 4: save_prediction
    Persists prediction results and telemetry state into SQLite database.
    """
    pred_id = f"pred-{int(datetime.utcnow().timestamp() * 1000)}"
    
    rec = PredictionRecord(
        id=pred_id,
        vehicle_id=vehicle_id,
        risk_level=prediction_data.get("riskLevel", "LOW"),
        probability=float(prediction_data.get("probability", 0.0)),
        maintenance_required=prediction_data.get("maintenanceRequired", "NO"),
        affected_subsystems=json.dumps(prediction_data.get("affectedAreas", [])),
        input_features=json.dumps(prediction_data.get("inputs", {})),
        created_at=datetime.utcnow()
    )
    try:
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return {"status": "saved", "id": pred_id}
    except Exception as e:
        db.rollback()
        return {"status": "error", "error": str(e), "id": pred_id}

def search_tavily_bulletins_tool(make: str, model: str, year: int, query: str) -> List[str]:
    """
    Optional Tavily Search Tool:
    Retrieves live technical service bulletins (TSB) and OEM maintenance advisories
    when TAVILY_API_KEY is configured.
    """
    if not settings.TAVILY_API_KEY or settings.TAVILY_API_KEY.strip() == "":
        return []

    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=settings.TAVILY_API_KEY)
        search_query = f"{year} {make} {model} technical service bulletin recall maintenance issues {query}"
        response = client.search(query=search_query, max_results=2)
        insights = []
        for res in response.get("results", []):
            insights.append(f"{res.get('title', '')}: {res.get('content', '')[:200]}...")
        return insights
    except Exception as e:
        # Graceful fallback if network or quota issue
        return [f"Tavily search skipped ({str(e)})"]
