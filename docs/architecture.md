# VehicleCare AI: System Architecture Document

## 1. High-Level Architectural Pattern
VehicleCare AI follows a **Layered Service-Oriented Architecture (SOA)** with clear separation of concerns across:
1. **Presentation Layer (Frontend Client):** Single Page Application written in React 18 with Tailwind CSS, Lucide React icons, and Recharts visualization.
2. **API & Orchestration Layer (FastAPI):** High-performance asynchronous REST API handling CORS, Pydantic validation, dependency injection, and router modularity.
3. **Agentic AI & Tool Layer:** Autonomous agent orchestrator coordinating domain tools, integrating Groq Llama-3.3 LLM inference and Tavily real-time OEM search, with local fallback logic.
4. **Machine Learning Layer (Scikit-Learn):** Calibrated Random Forest Classifier, dataset generation, metric computation, and model persistence via Joblib.
5. **Persistence Layer (SQLite + SQLAlchemy 2.0):** Relational database managing vehicles, maintenance logs, predictions, and datasets.

```
       [ Client Browser: React 18 + Tailwind CSS + Recharts ]
                                |
                   HTTP/JSON /api Endpoints
                                v
               [ FastAPI Application Gateway ]
           /           |               |            \
          v            v               v             v
   [Vehicles]     [Predict]         [Agent]     [Maintenance]
      CRUD       Scikit-Learn       Workflow        CRUD
        |             |                |              |
        v             v                v              v
   +------------------------------------------------------+
   |              SQLite Database (SQLAlchemy)            |
   +------------------------------------------------------+
```

## 2. Component Breakdown

### Frontend Client
- Single HTML/React bundle executing in the browser without complex node build chains, making it frictionless to present during university vivas.
- Real-time connection status check against `GET /api/health`.
- Graceful offline fallback if backend is stopped.

### FastAPI REST Layer
- Modular route division:
  - `routes/health.py`: Liveness and readiness probes.
  - `routes/vehicles.py`: Vehicle profile and telemetry state.
  - `routes/predict.py`: Scikit-Learn model execution.
  - `routes/agent.py`: Agentic AI tool execution.
  - `routes/maintenance.py`: Service record management.
  - `routes/dataset.py`: Dataset upload, schema validation, and retraining.
  - `routes/model.py`: Model performance metrics and feature importances.

### Machine Learning Pipeline
- Model: `RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)`
- Input: 8-dimensional telemetry vector.
- Output: Binary classification target (`maintenance_required`) and probability score.
- Metrics: Accuracy, Precision, Recall, F1-Score, Confusion Matrix, and Gini Feature Importance.

### Agentic AI Pipeline
- Sequentially checks telemetry constraints and invokes 5 distinct tools.
- Uses Groq for ultra-low-latency LLM synthesis or internal expert rules.
- Optionally queries Tavily for Technical Service Bulletins.
