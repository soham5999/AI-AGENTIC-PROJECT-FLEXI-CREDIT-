import json
import joblib
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from datetime import datetime
from app.config import settings
from app.ml.dataset_generator import FEATURE_COLUMNS, TARGET_COLUMN, generate_synthetic_dataset

_cached_model = None
_cached_metrics = None

def train_model(df: pd.DataFrame = None, model_save_path: str = None, metrics_save_path: str = None) -> Dict[str, Any]:
    """
    Trains a Scikit-Learn Random Forest Classifier on telemetry data,
    evaluates its performance on a held-out test split, and persists the model & metrics.
    """
    global _cached_model, _cached_metrics
    
    if df is None:
        dataset_path = Path(settings.DATASET_PATH)
        if dataset_path.exists():
            df = pd.read_csv(dataset_path)
        else:
            df = generate_synthetic_dataset(n_samples=600)
            dataset_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(dataset_path, index=False)

    # Validate required columns
    missing_cols = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset missing required feature columns: {missing_cols}")
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Dataset missing target column '{TARGET_COLUMN}'")

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN].astype(int)

    # Stratified Train/Test Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Initialize and fit Random Forest Classifier
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train, y_train)

    # Evaluate predictions
    y_pred = rf.predict(X_test)
    acc = round(accuracy_score(y_test, y_pred) * 100, 1)
    prec = round(precision_score(y_test, y_pred, zero_division=0) * 100, 1)
    rec = round(recall_score(y_test, y_pred, zero_division=0) * 100, 1)
    f1 = round(f1_score(y_test, y_pred, zero_division=0) * 100, 1)

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

    # Calculate Normalized Feature Importances
    importances = rf.feature_importances_
    total_imp = importances.sum() or 1.0
    feature_imp_list = [
        {
            "feature": col.replace("_", " ").upper(),
            "importance": int(round((imp / total_imp) * 100))
        }
        for col, imp in sorted(zip(FEATURE_COLUMNS, importances), key=lambda x: x[1], reverse=True)
    ]

    metrics_payload = {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1Score": f1,
        "confusionMatrix": {
            "truePositives": int(tp),
            "falsePositives": int(fp),
            "trueNegatives": int(tn),
            "falseNegatives": int(fn)
        },
        "featureImportances": feature_imp_list,
        "sampleSize": len(df),
        "trainSize": len(X_train),
        "testSize": len(X_test),
        "modelType": "Random Forest Classifier (Scikit-Learn)",
        "lastTrained": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }

    # Persist model artifact
    save_path = Path(model_save_path or settings.MODEL_PATH)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(rf, save_path)

    # Persist metrics JSON
    metrics_path = Path(metrics_save_path or settings.METRICS_PATH)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with open(metrics_path, "w") as f:
        json.dump(metrics_payload, f, indent=2)

    _cached_model = rf
    _cached_metrics = metrics_payload

    return metrics_payload

def load_model():
    """Loads the trained Random Forest model from disk (with caching)."""
    global _cached_model
    if _cached_model is not None:
        return _cached_model

    path = Path(settings.MODEL_PATH)
    if not path.exists():
        # Train model if not existing yet
        train_model()
        return _cached_model

    _cached_model = joblib.load(path)
    return _cached_model

def get_metrics() -> Dict[str, Any]:
    """Retrieves the latest model evaluation metrics."""
    global _cached_metrics
    if _cached_metrics is not None:
        return _cached_metrics

    path = Path(settings.METRICS_PATH)
    if not path.exists():
        return train_model()

    with open(path, "r") as f:
        _cached_metrics = json.load(f)
    return _cached_metrics

def evaluate_model():
    """Returns the cached or newly trained model evaluation metrics."""
    return get_metrics()
