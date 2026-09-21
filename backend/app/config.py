import os
from pathlib import Path
from dotenv import load_dotenv

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# Load .env file from project root or backend dir if present
load_dotenv(ROOT_DIR / ".env")
load_dotenv(BASE_DIR / ".env")

DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

class Settings:
    PROJECT_NAME: str = "VehicleCare AI"
    VERSION: str = "2.4.0"
    API_PREFIX: str = "/api"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    
    # SQLite Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/vehiclecare.db")
    
    # ML Model & Data paths
    MODEL_PATH: str = os.getenv("MODEL_PATH", str(MODELS_DIR / "vehicle_maintenance_rf.joblib"))
    METRICS_PATH: str = os.getenv("METRICS_PATH", str(MODELS_DIR / "model_metrics.json"))
    DATASET_PATH: str = os.getenv("DATASET_PATH", str(DATA_DIR / "synthetic_vehicle_data.csv"))
    
    # Groq & Tavily AI Agent Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    
    # Optional other LLMs
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    AI_MODEL_NAME: str = os.getenv("AI_MODEL_NAME", "llama-3.3-70b-versatile")

settings = Settings()
