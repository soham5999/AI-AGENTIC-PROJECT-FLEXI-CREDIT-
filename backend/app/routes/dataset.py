import io
import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pathlib import Path

from app.database import get_db
from app.config import settings
from app.ml.dataset_generator import FEATURE_COLUMNS, TARGET_COLUMN, generate_synthetic_dataset
from app.ml.trainer import train_model

router = APIRouter(prefix="/dataset", tags=["Dataset Management"])

@router.get("/current")
def get_current_dataset_summary():
    """Returns metadata and preview of the currently loaded training dataset."""
    dataset_path = Path(settings.DATASET_PATH)
    if not dataset_path.exists():
        df = generate_synthetic_dataset(n_samples=600)
        dataset_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(dataset_path, index=False)
    else:
        df = pd.read_csv(dataset_path)

    # Convert preview records
    preview_records = []
    for idx, row in df.head(15).iterrows():
        r = row.to_dict()
        r["id"] = int(idx) + 1
        preview_records.append(r)

    return {
        "filename": dataset_path.name,
        "totalRecords": len(df),
        "totalFeatures": len(FEATURE_COLUMNS),
        "targetColumn": TARGET_COLUMN,
        "missingValues": int(df.isnull().sum().sum()),
        "columns": list(df.columns),
        "preview": preview_records
    }

@router.post("/upload")
async def upload_custom_dataset(file: UploadFile = File(...)):
    """
    Receives a CSV or Excel dataset, validates schema and column types,
    persists the data, and automatically triggers Random Forest retraining.
    """
    if not file.filename.endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a .csv or .xlsx file."
        )

    content = await file.read()
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        else:
            df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if len(df) < 20:
        raise HTTPException(
            status_code=400,
            detail="Dataset contains insufficient rows (minimum 20 records required for machine learning train/test split)."
        )

    # Validate column requirements
    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Incompatible dataset columns. Missing required features: {missing}"
        )

    # Handle missing values
    df[FEATURE_COLUMNS] = df[FEATURE_COLUMNS].fillna(df[FEATURE_COLUMNS].mean())

    if TARGET_COLUMN not in df.columns:
        # Impute target if missing based on mechanical risk rules
        df[TARGET_COLUMN] = (
            (df["brake_wear_pct"] > 70) | (df["oil_life_pct"] < 25) | (df["days_since_service"] > 200)
        ).astype(int)

    # Persist uploaded dataset
    save_path = Path(settings.DATASET_PATH)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(save_path, index=False)

    # Retrain Scikit-Learn Model
    metrics = train_model(df)

    preview_records = []
    for idx, row in df.head(15).iterrows():
        r = row.to_dict()
        r["id"] = int(idx) + 1
        preview_records.append(r)

    return {
        "status": "success",
        "message": f"Successfully processed '{file.filename}', validated {len(df)} records, and retrained Random Forest Classifier!",
        "filename": file.filename,
        "records": len(df),
        "features": len(FEATURE_COLUMNS),
        "metrics": metrics,
        "preview": preview_records
    }

@router.post("/reset-demo")
def reset_to_synthetic_dataset():
    """Resets the training dataset back to the standard synthetic baseline and retrains the model."""
    dataset_path = Path(settings.DATASET_PATH)
    df = generate_synthetic_dataset(n_samples=600)
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(dataset_path, index=False)

    # Retrain
    metrics = train_model(df)

    return {
        "status": "success",
        "message": "Reset to default synthetic dataset (600 records) and retrained ML model.",
        "metrics": metrics
    }
