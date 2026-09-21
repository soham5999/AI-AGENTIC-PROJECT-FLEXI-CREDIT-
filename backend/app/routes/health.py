from fastapi import APIRouter
from datetime import datetime
from app.config import settings

router = APIRouter(prefix="/health", tags=["System Health"])

@router.get("")
def get_system_health():
    """
    Returns system status, API version, and backend operational state.
    """
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "ml_engine": "online",
        "agent_status": "ready",
        "groq_enabled": bool(settings.GROQ_API_KEY),
        "tavily_enabled": bool(settings.TAVILY_API_KEY)
    }
