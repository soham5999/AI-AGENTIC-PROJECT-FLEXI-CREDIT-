from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class DatasetSummary(BaseModel):
    id: str
    filename: str
    records: int
    features: int
    target_column: str
    status: str
    uploaded_at: str

class ConfusionMatrixData(BaseModel):
    truePositives: int
    falsePositives: int
    trueNegatives: int
    falseNegatives: int

class FeatureImportanceItem(BaseModel):
    feature: str
    importance: int

class ModelMetricsOut(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1Score: float
    confusionMatrix: ConfusionMatrixData
    featureImportances: List[FeatureImportanceItem]
    sampleSize: int
    modelType: str = "Random Forest Classifier (Scikit-Learn)"
    lastTrained: Optional[str] = None
