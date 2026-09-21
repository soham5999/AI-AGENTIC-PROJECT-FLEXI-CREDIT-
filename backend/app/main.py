from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from contextlib import asynccontextmanager

from app.config import settings, ROOT_DIR
from app.database import engine, Base, SessionLocal
from app.models.vehicle import Vehicle
from app.models.maintenance import MaintenanceRecord
from app.ml.trainer import load_model, train_model
from app.routes import (
    health_router,
    vehicles_router,
    predict_router,
    agent_router,
    maintenance_router,
    dataset_router,
    model_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    # 1. Create SQLite database tables if not existing
    Base.metadata.create_all(bind=engine)

    # 2. Seed initial demo vehicle & maintenance logs if database is empty
    db = SessionLocal()
    try:
        demo_vehicle = db.query(Vehicle).filter(Vehicle.id == "v-camry-01").first()
        if not demo_vehicle:
            demo_vehicle = Vehicle(
                id="v-camry-01",
                make="Toyota",
                model="Camry Hybrid (Demo Fleet Vehicle)",
                year=2021,
                type="Sedan",
                mileage=62450,
                days_since_service=195,
                battery_voltage=11.9,
                engine_temp=99.0,
                brake_wear_pct=78.0,
                tire_pressure_avg=30.0,
                oil_life_pct=22.0
            )
            db.add(demo_vehicle)
            db.commit()

        # Seed initial maintenance records
        if db.query(MaintenanceRecord).count() == 0:
            demo_logs = [
                MaintenanceRecord(id="m-101", vehicle_id="v-camry-01", date="2025-11-12", mileage=58000, service_type="Synthetic Oil & Filter Change", cost=120, notes="Full synthetic 0W-20 replaced"),
                MaintenanceRecord(id="m-102", vehicle_id="v-camry-01", date="2025-06-04", mileage=51200, service_type="Brake Fluid Flush & Inspection", cost=185, notes="Brake pads measured at 45%"),
                MaintenanceRecord(id="m-103", vehicle_id="v-camry-01", date="2024-12-18", mileage=42000, service_type="Tire Rotation & Wheel Alignment", cost=95, notes="Balanced all four tires"),
                MaintenanceRecord(id="m-104", vehicle_id="v-camry-01", date="2024-05-10", mileage=31500, service_type="Battery System Diagnosis", cost=45, notes="Battery health verified good at 12.6V")
            ]
            db.add_all(demo_logs)
            db.commit()
    finally:
        db.close()

    # 3. Ensure ML Model is trained and cached
    try:
        load_model()
    except Exception:
        train_model()

    print(f"VehicleCare AI Backend initialized on {settings.HOST}:{settings.PORT}")
    print(f"Interactive Swagger Documentation available at http://localhost:{settings.PORT}/docs")
    yield

app = FastAPI(
    title="VehicleCare AI - Vehicle Maintenance Prediction API",
    description="Industry-grade AI-powered vehicle predictive maintenance intelligence engine with Scikit-Learn ML and Groq/Tavily Agentic AI tools.",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS middleware for cross-origin browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST API Routers
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(vehicles_router, prefix=settings.API_PREFIX)
app.include_router(predict_router, prefix=settings.API_PREFIX)
app.include_router(agent_router, prefix=settings.API_PREFIX)
app.include_router(maintenance_router, prefix=settings.API_PREFIX)
app.include_router(dataset_router, prefix=settings.API_PREFIX)
app.include_router(model_router, prefix=settings.API_PREFIX)

# Serve Frontend HTML
html_file_path = ROOT_DIR / "vehiclecare_ai_web_application.html"

@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
def serve_root():
    """Serves the main VehicleCare AI application UI."""
    if html_file_path.exists():
        return FileResponse(html_file_path)
    return HTMLResponse("<h2>VehicleCare AI Backend Online. Open Swagger docs at <a href='/docs'>/docs</a></h2>")

@app.get("/app", response_class=HTMLResponse, tags=["Frontend"])
def serve_app():
    """Serves the main VehicleCare AI application UI."""
    if html_file_path.exists():
        return FileResponse(html_file_path)
    return HTMLResponse("<h2>VehicleCare AI UI not found on disk.</h2>")
