import numpy as np
import pandas as pd
from pathlib import Path
from app.config import settings

FEATURE_COLUMNS = [
    "vehicle_age",
    "odometer_km",
    "days_since_service",
    "battery_voltage",
    "engine_temp",
    "brake_wear_pct",
    "tire_pressure_avg",
    "oil_life_pct"
]

TARGET_COLUMN = "maintenance_required"

def generate_synthetic_dataset(n_samples: int = 500, random_state: int = 42) -> pd.DataFrame:
    """
    Generate a physically realistic synthetic dataset for vehicle predictive maintenance.
    Simulates real automotive engineering correlations:
      - High brake wear (>70%) significantly triggers maintenance need
      - Low oil life (<20%) or long service interval (>180 days) triggers service need
      - Degraded battery (<11.9V) or engine overheating (>100C) contributes to risk
    """
    rng = np.random.RandomState(random_state)
    
    # Generate realistic base features
    vehicle_age = rng.uniform(0.5, 12.0, size=n_samples) # 0.5 to 12 years
    odometer_km = vehicle_age * rng.normal(14000, 2500, size=n_samples) + rng.uniform(2000, 10000, size=n_samples)
    odometer_km = np.clip(odometer_km, 3000, 300000).round()
    
    days_since_service = rng.exponential(scale=110, size=n_samples) + rng.uniform(10, 45, size=n_samples)
    days_since_service = np.clip(days_since_service, 5, 450).round()
    
    # Battery voltage: healthy is 12.4 - 12.8V, degraded is 11.2 - 12.1V
    battery_voltage = rng.normal(12.35, 0.45, size=n_samples)
    battery_voltage = np.clip(battery_voltage, 11.0, 13.2).round(2)
    
    # Engine temp: normal operating is 86 - 96C, hot is 98 - 115C
    engine_temp = rng.normal(91.0, 6.5, size=n_samples)
    engine_temp = np.clip(engine_temp, 75.0, 118.0).round(1)
    
    # Brake wear percentage: increases with mileage and time
    base_wear = (odometer_km % 45000) / 45000.0 * 100.0
    brake_wear_pct = np.clip(base_wear + rng.normal(0, 12, size=n_samples), 5.0, 98.0).round(1)
    
    # Tire pressure: normal is 32 - 34 PSI
    tire_pressure_avg = rng.normal(32.5, 3.2, size=n_samples)
    tire_pressure_avg = np.clip(tire_pressure_avg, 22.0, 44.0).round(1)
    
    # Oil life percentage: decreases as days_since_service increases
    oil_drain = np.clip(days_since_service / 200.0 * 100.0, 0, 100)
    oil_life_pct = np.clip(100.0 - oil_drain + rng.normal(0, 10, size=n_samples), 2.0, 100.0).round(1)
    
    # Realistic mechanical failure risk scoring function
    risk_score = np.zeros(n_samples)
    
    risk_score += np.where(brake_wear_pct > 80, 40, np.where(brake_wear_pct > 65, 25, 0))
    risk_score += np.where(oil_life_pct < 15, 35, np.where(oil_life_pct < 30, 20, 0))
    risk_score += np.where(days_since_service > 220, 25, np.where(days_since_service > 180, 15, 0))
    risk_score += np.where(battery_voltage < 11.85, 25, np.where(battery_voltage < 12.2, 12, 0))
    risk_score += np.where(engine_temp > 102, 25, np.where(engine_temp > 97, 12, 0))
    risk_score += np.where((tire_pressure_avg < 28) | (tire_pressure_avg > 38), 12, 0)
    risk_score += np.where(odometer_km > 120000, 10, 0)
    
    # Add small stochastic variation (mechanical uncertainty)
    risk_score += rng.normal(0, 5, size=n_samples)
    
    # Target label: 1 if maintenance recommended (score >= 50), 0 otherwise
    maintenance_required = (risk_score >= 48).astype(int)
    
    df = pd.DataFrame({
        "vehicle_age": vehicle_age.round(1),
        "odometer_km": odometer_km.astype(int),
        "days_since_service": days_since_service.astype(int),
        "battery_voltage": battery_voltage,
        "engine_temp": engine_temp,
        "brake_wear_pct": brake_wear_pct,
        "tire_pressure_avg": tire_pressure_avg,
        "oil_life_pct": oil_life_pct,
        "maintenance_required": maintenance_required
    })
    
    return df

def save_default_dataset(filepath: str = None) -> str:
    """Generates and persists the default synthetic dataset to disk."""
    path = Path(filepath or settings.DATASET_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = generate_synthetic_dataset(n_samples=600)
    df.to_csv(path, index=False)
    return str(path)
