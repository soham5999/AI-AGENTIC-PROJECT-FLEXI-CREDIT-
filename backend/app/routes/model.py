from fastapi import APIRouter
from app.schemas.dataset import ModelMetricsOut
from app.ml.trainer import get_metrics, train_model

router = APIRouter(prefix="/model", tags=["Model Performance & MLOps"])

@router.get("/performance", response_model=ModelMetricsOut)
def get_model_performance():
    """
    Returns current Scikit-Learn Random Forest Classifier evaluation metrics:
    Accuracy, Precision, Recall, F1-Score, Confusion Matrix, and Gini Feature Importances.
    """
    metrics = get_metrics()
    return metrics

@router.post("/retrain", response_model=ModelMetricsOut)
def retrain_model_endpoint():
    """Triggers an explicit retraining cycle of the Random Forest model."""
    metrics = train_model()
    return metrics
