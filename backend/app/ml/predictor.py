from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from app.ml.trainer import load_model, get_metrics
from app.ml.dataset_generator import FEATURE_COLUMNS

def calculate_subsystem_health(v: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Evaluates individual vehicle mechanical subsystems based on telemetry thresholds.
    """
    affected = []
    brake = float(v.get("brake_wear_pct", 0))
    oil = float(v.get("oil_life_pct", 100))
    voltage = float(v.get("battery_voltage", 12.6))
    days = float(v.get("days_since_service", 0))
    temp = float(v.get("engine_temp", 90))
    tire = float(v.get("tire_pressure_avg", 32))

    if brake >= 65:
        severity = "Critical" if brake > 80 else "Moderate"
        affected.append({
            "name": "Brake System",
            "severity": severity,
            "detail": f"Brake pad friction material worn down to {brake}% (Safety limit: 65%)"
        })

    if oil <= 25:
        severity = "Critical" if oil < 15 else "Moderate"
        affected.append({
            "name": "Engine Lubrication",
            "severity": severity,
            "detail": f"Engine oil viscosity degraded, only {oil}% remaining life"
        })

    if voltage <= 12.1:
        severity = "Critical" if voltage < 11.8 else "Moderate"
        affected.append({
            "name": "Electrical & Battery",
            "severity": severity,
            "detail": f"Alternator/battery voltage low at {voltage}V (Healthy > 12.4V)"
        })

    if days >= 180:
        severity = "Critical" if days > 240 else "Moderate"
        affected.append({
            "name": "Routine Service Interval",
            "severity": severity,
            "detail": f"{int(days)} days elapsed since last certified workshop inspection"
        })

    if temp >= 98:
        severity = "Critical" if temp > 105 else "Moderate"
        affected.append({
            "name": "Cooling System",
            "severity": severity,
            "detail": f"Coolant operating temperature elevated at {temp}°C (Normal: 86-94°C)"
        })

    if tire < 29 or tire > 37:
        severity = "Moderate" if tire < 26 or tire > 40 else "Low"
        affected.append({
            "name": "Tires & Pressure",
            "severity": severity,
            "detail": f"Mean tire pressure is {tire} PSI (Recommended: 32 PSI)"
        })

    return affected

def predict_maintenance(features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the trained Scikit-Learn Random Forest Classifier model
    on the vehicle telemetry vector.
    """
    model = load_model()

    # Build input feature vector in exact order
    input_df = pd.DataFrame([{
        col: float(features.get(col, 0.0)) for col in FEATURE_COLUMNS
    }])

    # Predict class and probability
    probabilities = model.predict_proba(input_df)[0]
    
    # Class 1 probability is the probability of maintenance required
    if len(probabilities) > 1:
        prob_maintenance = float(probabilities[1])
    else:
        prob_maintenance = float(probabilities[0])

    prob_percentage = round(prob_maintenance * 100, 1)

    # Determine risk category
    if prob_percentage >= 70:
        risk_level = "HIGH"
    elif prob_percentage >= 35:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    maintenance_required = "YES" if prob_percentage >= 50 else "NO"
    affected_subsystems = calculate_subsystem_health(features)

    # Get feature importances for explainability
    metrics = get_metrics()
    feature_importances = metrics.get("featureImportances", [])

    return {
        "probability": prob_percentage,
        "riskLevel": risk_level,
        "maintenanceRequired": maintenance_required,
        "affectedAreas": affected_subsystems,
        "featureImportances": feature_importances,
        "inputs": features,
        "model_version": "RandomForest-v2.4"
    }
