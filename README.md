# VehicleCare AI: AI Agent for Vehicle Maintenance Prediction

> **CA3 Mini Project**  
> **Course:** B.Tech Computer Science and Engineering (Data Science)  
> **Topic:** Agentic AI & Machine Learning for Predictive Automotive Telemetry  

---

## 1. Project Title & Overview
**VehicleCare AI** is an industry-inspired, end-to-end intelligent predictive maintenance platform. It ingests automotive sensor telemetry, runs a calibrated **Scikit-Learn Random Forest Classifier** to assess component failure risks, and orchestrates an **Agentic AI Diagnostic Engine** equipped with autonomous tools to synthesize maintenance actions, assess urgency, and cross-reference OEM technical bulletins.

---

## 2. Problem Statement
Traditional automotive maintenance follows two outdated models:
1. **Reactive Maintenance (Run-to-Failure):** Repairing components only after they break, resulting in costly roadside breakdowns, secondary mechanical damage, and severe safety hazards.
2. **Static Scheduled Maintenance (Mileage/Calendar-based):** Servicing vehicles strictly every 10,000 km or 6 months, ignoring actual driving patterns, wear rates, and harsh operating conditions.

**Predictive Maintenance with Agentic AI** solves this by continuously analyzing real-time sensor metrics (brake wear, engine temperature, oil viscosity, battery voltage, and usage intervals) to forecast mechanical degradation *before* failure occurs, delivering prioritized, human-actionable advice.

---

## 3. System Architecture

```
+-----------------------------------------------------------------------------------+
|                           VEHICLECARE AI FRONTEND                                 |
|            (React 18 + Tailwind CSS + Lucide Icons + Recharts Analytics)          |
|   Dashboard  |  My Vehicle  |  AI Predictor  |  AI Agent  |  Dataset  |  Metrics  |
+------------------------------------------+----------------------------------------+
                                           | REST API (JSON / HTTP)
                                           v
+-----------------------------------------------------------------------------------+
|                        FASTAPI BACKEND ENGINE (Port 8000)                         |
|                                                                                   |
|  +------------------------+  +------------------------+  +---------------------+  |
|  |     REST API Layer     |  |   Database ORM Layer   |  |   Data Preprocessing|  |
|  | /predict, /agent, etc. |  |   SQLAlchemy + SQLite  |  |  Pandas, Validation |  |
|  +-----------+------------+  +-----------+------------+  +----------+----------+  |
|              |                           |                          |             |
|              v                           v                          v             |
|  +-----------------------------------------------------------------------------+  |
|  |                        AGENTIC AI ORCHESTRATOR WORKFLOW                     |  |
|  |                                                                             |  |
|  |   Tool 5: get_vehicle_information  ---> Queries SQLite vehicle record       |  |
|  |   Tool 1: predict_vehicle_maintenance -> Executes Scikit-Learn RF Model     |  |
|  |   Tool 2: analyze_vehicle_health   ---> Checks Subsystem Sensor Thresholds  |  |
|  |   Tool 3: get_maintenance_history ---> Retrieves Historical Service Records |  |
|  |   Tool 4: save_prediction         ---> Persists Output & Risk Assessment   |  |
|  |   (Optional) search_tavily_bulletins -> Real-Time OEM Technical Advisories   |  |
|  +---------------------------------------+-------------------------------------+  |
|                                          |                                        |
|                     +--------------------+--------------------+                   |
|                     |                                         |                   |
|                     v                                         v                   |
|       +---------------------------+             +---------------------------+     |
|       |     GROQ LLM INFERENCE    |             |    DEMO FALLBACK AGENT    |     |
|       |  (Llama-3.3-70b-versatile)|             | (Local Heuristic Engine)  |     |
|       |   Natural language agent  |             |  Zero-dependency viva mode|     |
|       +---------------------------+             +---------------------------+     |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                         MACHINE LEARNING SUBSYSTEM                          |  |
|  |  * Algorithm: Random Forest Classifier (n_estimators=100, max_depth=12)     |  |
|  |  * Metrics: Accuracy: 90.8% | Precision: 87.2% | Recall: 89.1% | F1: 88.2% |  |
|  |  * Storage: vehicle_maintenance_rf.joblib, model_metrics.json              |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 4. Key Features

- **Dynamic Machine Learning Prediction:** Real-time inference using Scikit-Learn Random Forest Classifier trained on telemetry datasets.
- **Autonomous AI Agent with 5 Real Tools:**
  1. `predict_vehicle_maintenance`: Calls the ML model.
  2. `analyze_vehicle_health`: Evaluates sensor safety thresholds (brakes, battery, oil, cooling).
  3. `get_maintenance_history`: Retrieves historical logs from SQLite.
  4. `save_prediction`: Persists diagnostic predictions.
  5. `get_vehicle_information`: Loads telemetry parameters from SQLite.
- **Dual Agent Engine (Groq + Fallback):**
  - **Groq API Support:** Ultra-fast reasoning powered by `llama-3.3-70b-versatile`.
  - **Tavily API Integration:** Real-time web retrieval for OEM technical service bulletins.
  - **Local Fallback Engine:** 100% offline demonstration mode when no API keys are configured.
- **Persistent SQLite Database:** SQLAlchemy models for Vehicles, Maintenance Records, Predictions, and Datasets.
- **Dataset Management & Retraining:** Upload custom CSV/Excel telemetry files with automated validation and on-the-fly model retraining.
- **Model Performance Dashboard:** Live Accuracy, Precision, Recall, F1 Score, Confusion Matrix, and Gini Feature Importances.
- **Interactive OpenAPI / Swagger Inspector:** Test live endpoints right from the UI modal or visit `/docs`.

---

## 5. Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Frontend** | React 18, Tailwind CSS, Recharts 2.10, Lucide Icons, Babel |
| **Backend** | Python 3.13, FastAPI, Uvicorn, Pydantic v2, Pydantic-Settings |
| **Database** | SQLite, SQLAlchemy 2.0 ORM |
| **Machine Learning** | Scikit-Learn, Pandas, NumPy, Joblib |
| **AI Agent & LLM** | Groq Python SDK (Llama 3.3), Tavily API, Custom Agentic Tool Pipeline |

---

## 6. Telemetry Features & ML Model

### Telemetry Features
1. `vehicle_age`: Age of vehicle in years (0.5 to 15 yrs)
2. `odometer_km`: Total distance driven in kilometers
3. `days_since_service`: Days elapsed since last certified workshop inspection
4. `battery_voltage`: Resting terminal voltage (11.0V to 13.2V)
5. `engine_temp`: Coolant operating temperature (75°C to 118°C)
6. `brake_wear_pct`: Brake pad wear percentage (0% to 100%)
7. `tire_pressure_avg`: Mean tire pressure in PSI (22 to 44 PSI)
8. `oil_life_pct`: Estimated remaining oil viscosity life (0% to 100%)

### Target Variable
- `maintenance_required`: `1` (Service required) or `0` (Normal)

### Current Trained Model Performance
- **Accuracy:** 90.8%
- **Precision:** 87.2%
- **Recall:** 89.1%
- **F1-Score:** 88.2%
- **Top Feature Contributors:** `days_since_service` (33%), `oil_life_pct` (31%), `brake_wear_pct` (16%).

---

## 7. Installation & Quick Start

### Prerequisites
- Python 3.10+ installed
- Git (optional)

### 1. Clone or Open Workspace
```bash
cd "C:\Users\hp\Desktop\FLEXI CA3"
```

### 2. Install Python Dependencies
```bash
pip install -r backend/requirements.txt
```

### 3. Configure Environment Variables (Optional)
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
*(Optional: add your `GROQ_API_KEY` and `TAVILY_API_KEY`. If left empty, the project automatically runs in high-performance local demo mode.)*

### 4. Initialize Database & Train Initial Model
```bash
python backend/seed_data.py
```

### 5. Start the FastAPI Server
```bash
python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```
Or simply double-click **`run_backend.bat`** on Windows!

---

## 8. Accessing the Application

- **Web Dashboard:** Open [http://localhost:8000](http://localhost:8000) or open `vehiclecare_ai_web_application.html` directly in any browser.
- **FastAPI Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **FastAPI Redoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 9. API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | System health, database connection, and AI status |
| `GET` | `/api/vehicles` | List all vehicles in SQLite |
| `GET` | `/api/vehicles/default/demo` | Get default demo vehicle |
| `PUT` | `/api/vehicles/{id}` | Update vehicle sensor telemetry |
| `POST` | `/api/predict` | Run Scikit-Learn Random Forest prediction |
| `POST` | `/api/agent/analyze` | Execute Agentic AI diagnostic workflow |
| `GET` | `/api/maintenance/{vehicle_id}` | List maintenance history |
| `POST` | `/api/maintenance` | Add new maintenance service record |
| `DELETE`| `/api/maintenance/{id}` | Delete service record |
| `GET` | `/api/model/performance` | Get ML metrics, confusion matrix, feature importances |
| `POST` | `/api/dataset/upload` | Upload custom CSV/XLSX and retrain model |
| `POST` | `/api/dataset/reset-demo` | Reset to baseline synthetic dataset |

---

## 10. Future Scope
- **OBD-II Dongle Integration:** Real-time streaming of live vehicle CAN bus PID codes via Bluetooth/Wi-Fi.
- **IoT Telematics Edge Gateway:** ESP32/Raspberry Pi gateway with MQTT protocol.
- **Fleet Management Dashboard:** Multi-vehicle fleet dispatch and anomaly alerts.
- **Survival Analysis & Remaining Useful Life (RUL):** Estimating exact kilometers remaining before critical part failure using Weibull analysis.
