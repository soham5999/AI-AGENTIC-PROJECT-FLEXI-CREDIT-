from app.routes.health import router as health_router
from app.routes.vehicles import router as vehicles_router
from app.routes.predict import router as predict_router
from app.routes.agent import router as agent_router
from app.routes.maintenance import router as maintenance_router
from app.routes.dataset import router as dataset_router
from app.routes.model import router as model_router

__all__ = [
    "health_router",
    "vehicles_router",
    "predict_router",
    "agent_router",
    "maintenance_router",
    "dataset_router",
    "model_router"
]
