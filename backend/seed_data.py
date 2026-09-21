"""
Database Seeder & ML Model Initialization Script
Initializes SQLite database tables, seeds demo fleet records,
and trains the baseline Scikit-Learn Random Forest Classifier.
"""
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.database import engine, Base, SessionLocal
from app.models.vehicle import Vehicle
from app.models.maintenance import MaintenanceRecord
from app.ml.dataset_generator import save_default_dataset
from app.ml.trainer import train_model

def seed_database():
    print("=" * 60)
    print("VehicleCare AI - Database Seeding & Model Training")
    print("=" * 60)

    # 1. Create tables
    print("[1/4] Creating SQLite database tables...")
    Base.metadata.create_all(bind=engine)
    print("      SQLite database tables initialized successfully.")

    # 2. Seed default demo vehicle
    print("[2/4] Seeding demo fleet vehicle...")
    db = SessionLocal()
    try:
        existing = db.query(Vehicle).filter(Vehicle.id == "v-camry-01").first()
        if not existing:
            v = Vehicle(
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
            db.add(v)
            db.commit()
            print("      Created default demo vehicle: Toyota Camry Hybrid (ID: v-camry-01)")
        else:
            print("      Demo vehicle already exists.")

        # 3. Seed maintenance logs
        print("[3/4] Seeding initial maintenance logs...")
        if db.query(MaintenanceRecord).count() == 0:
            demo_logs = [
                MaintenanceRecord(id="m-101", vehicle_id="v-camry-01", date="2025-11-12", mileage=58000, service_type="Synthetic Oil & Filter Change", cost=120, notes="Full synthetic 0W-20 replaced"),
                MaintenanceRecord(id="m-102", vehicle_id="v-camry-01", date="2025-06-04", mileage=51200, service_type="Brake Fluid Flush & Inspection", cost=185, notes="Brake pads measured at 45%"),
                MaintenanceRecord(id="m-103", vehicle_id="v-camry-01", date="2024-12-18", mileage=42000, service_type="Tire Rotation & Wheel Alignment", cost=95, notes="Balanced all four tires"),
                MaintenanceRecord(id="m-104", vehicle_id="v-camry-01", date="2024-05-10", mileage=31500, service_type="Battery System Diagnosis", cost=45, notes="Battery health verified good at 12.6V")
            ]
            db.add_all(demo_logs)
            db.commit()
            print(f"      Seeded {len(demo_logs)} historical service records.")
        else:
            print("      Maintenance records already exist.")
    finally:
        db.close()

    # 4. Generate dataset and train Random Forest Classifier
    print("[4/4] Generating synthetic telemetry dataset & training Random Forest Classifier...")
    csv_path = save_default_dataset()
    print(f"      Synthetic dataset generated at: {csv_path}")

    metrics = train_model()
    print("\n" + "-" * 50)
    print("Scikit-Learn Random Forest Classifier Trained:")
    print(f"  - Accuracy  : {metrics['accuracy']}%")
    print(f"  - Precision : {metrics['precision']}%")
    print(f"  - Recall    : {metrics['recall']}%")
    print(f"  - F1-Score  : {metrics['f1Score']}%")
    print(f"  - Test Size : {metrics['testSize']} samples")
    print("-" * 50)
    print("Top Predictive Telemetry Features:")
    for feat in metrics["featureImportances"][:5]:
        print(f"  * {feat['feature']:<20}: {feat['importance']}%")
    print("=" * 60)
    print("Seeding complete! Backend is ready to run.")
    print("=" * 60)

if __name__ == "__main__":
    seed_database()
