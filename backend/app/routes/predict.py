from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.schemas.prediction import PredictionInput, PredictionOut
from app.ml.predictor import predict_maintenance
from app.agent.tools import save_prediction_tool

router = APIRouter(prefix="/predict", tags=["ML Predictions"])

@router.post("", response_model=PredictionOut)
def run_prediction_endpoint(input_data: PredictionInput, db: Session = Depends(get_db)):
    """
    Executes the Scikit-Learn Random Forest Classifier model
    on user-submitted vehicle telemetry features and persists the result.
    """
    features = input_data.dict()
    vehicle_id = features.pop("vehicle_id", None) or "v-camry-01"

    # ML Inference
    result = predict_maintenance(features)

    # Persist prediction in SQLite
    save_info = save_prediction_tool(vehicle_id, result, db)

    response_payload = {
        "id": save_info.get("id", f"pred-{int(datetime.utcnow().timestamp()*1000)}"),
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "probability": result["probability"],
        "riskLevel": result["riskLevel"],
        "maintenanceRequired": result["maintenanceRequired"],
        "affectedAreas": result["affectedAreas"],
        "featureImportances": result.get("featureImportances"),
        "inputs": features,
        "model_version": result.get("model_version", "RandomForest-v2.4")
    }

    return response_payload
