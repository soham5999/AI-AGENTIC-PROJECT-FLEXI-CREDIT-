# CA3 Mini Project Viva Preparation & Concepts Guide

> **Degree:** B.Tech Computer Science and Engineering (Data Science)  
> **Course:** CA3 Assessment  
> **Project:** AI Agent for Vehicle Maintenance Prediction (VehicleCare AI)  

---

### Q1: What is an AI Agent?
**Answer:** An AI Agent is an autonomous software entity that perceives its environment (e.g., telemetry inputs, database records), reasons over this context using an LLM or decision policy, and takes goal-directed actions by executing software tools (functions, APIs, or database operations) to produce actionable outcomes.

---

### Q2: Why is this project called "Agentic AI" rather than just Machine Learning?
**Answer:** In pure Machine Learning, a model only computes a static probability (e.g. `0.85`). An **Agentic AI** project wraps this model inside an autonomous workflow:
1. It validates whether sufficient vehicle parameters exist.
2. It calls external tools (`predict_vehicle_maintenance`, `analyze_vehicle_health`, `get_maintenance_history`).
3. It cross-examines individual sensor thresholds.
4. It synthesizes natural language diagnostic reasoning and prioritizes action items with specific urgency timeframes (e.g., *"Replace brake pads within 3 days"*).

---

### Q3: What is the fundamental difference between an ML Model and an AI Agent?
**Answer:**
- **ML Model (Random Forest):** A statistical pattern recognizer trained on historical data that maps numerical input vectors to a class or probability score. It has no autonomy and cannot interact with databases or make decisions on its own.
- **AI Agent:** The orchestrator that *uses* the ML model as one of its tools, queries the database, checks physical rules, queries external information (like OEM Technical Service Bulletins via Tavily), and communicates with the human user in natural language.

---

### Q4: Why was Random Forest Classifier chosen over Deep Learning or Linear Models?
**Answer:**
1. **Tabular Data Superiority:** Tree ensembles (Random Forests, XGBoost) consistently outperform deep neural networks on tabular datasets with non-linear feature boundaries without requiring extensive hyperparameter tuning.
2. **Interpretability:** Random Forest provides built-in Gini feature importance, explaining which sensor features (e.g. `days_since_service`, `oil_life_pct`) contributed most to the prediction.
3. **Robustness to Outliers & Overfitting:** By averaging predictions over 100 decorrelated decision trees trained on bootstrap samples, variance and overfitting are significantly minimized.
4. **Low Latency on Edge CPUs:** Computes inference in milliseconds without requiring expensive GPU infrastructure.

---

### Q5: What is Predictive Maintenance (PdM) versus Preventive and Reactive Maintenance?
**Answer:**
- **Reactive (Corrective):** Fix it when it breaks. Causes unexpected breakdowns and high repair costs.
- **Preventive (Time-based):** Fix it on a fixed schedule (e.g., every 10,000 km) regardless of whether the part is worn. Leads to wasteful early replacements or failures between schedules.
- **Predictive (Condition-based):** Continuous monitoring of telemetry sensor metrics to forecast the exact degradation state and service parts *just before* critical failure occurs.

---

### Q6: What vehicle features are used in the prediction model?
**Answer:** Eight physical engineering features:
1. `vehicle_age`: Age of vehicle in years.
2. `odometer_km`: Total distance driven.
3. `days_since_service`: Time elapsed since certified service.
4. `battery_voltage`: Electrical system voltage (Healthy: >12.4V; Degraded: <11.8V).
5. `engine_temp`: Coolant temperature (Normal: 86–94°C; Overheating: >102°C).
6. `brake_wear_pct`: Brake pad wear percentage (Threshold: 65%).
7. `tire_pressure_avg`: Average tire PSI (Normal: 30–34 PSI).
8. `oil_life_pct`: Viscosity life percentage (Threshold: <20%).

---

### Q7: How does the AI Agent call the ML Model?
**Answer:** The AI Agent exposes a Python tool function named `predict_vehicle_maintenance(features)`. When the agent executes its workflow, it passes the 8-dimensional telemetry dictionary to this tool. The tool loads the cached Scikit-Learn Joblib model artifact (`vehicle_maintenance_rf.joblib`), passes the feature vector to `model.predict_proba()`, and returns the probability percentage and risk classification to the agent.

---

### Q8: What are the 5 Tools used by the AI Agent?
**Answer:**
1. `predict_vehicle_maintenance`: Invokes Scikit-Learn Random Forest inference.
2. `analyze_vehicle_health`: Analyzes safety thresholds across battery, brakes, oil, cooling, and tires.
3. `get_maintenance_history`: Retrieves historical maintenance records from SQLite.
4. `save_prediction`: Persists diagnostic predictions to SQLite for trend tracking.
5. `get_vehicle_information`: Queries vehicle telemetry from SQLite by ID.
*(Bonus tool: `search_tavily_bulletins` retrieves OEM Technical Service Bulletins from the web).*

---

### Q9: How does the Demo / Fallback mode work if no API key is provided?
**Answer:** In production, Groq API (`llama-3.3-70b-versatile`) is called to synthesize the tool results into natural language. If no `GROQ_API_KEY` is provided in `.env`, the system automatically activates the **Demo Rule-Based Fallback Agent**. This agent applies automotive engineering heuristics to the tool outputs, generating structured reasoning, health scores, and prioritized action items with zero external dependencies.

---

### Q10: How does the Dataset Upload and Retraining work?
**Answer:**
1. The user uploads a CSV or Excel file through `POST /api/dataset/upload`.
2. Pandas parses the file and validates the required 8 feature columns and target variable.
3. Missing values are imputed using column means.
4. An 80/20 train/test split is performed.
5. Scikit-Learn's `RandomForestClassifier` is retrained, evaluation metrics (Accuracy, Precision, Recall, F1) are recalculated, the new model is saved via `joblib.dump()`, and the UI is updated immediately.

---

### Q11: What are Accuracy, Precision, Recall, and F1-Score in this context?
**Answer:**
- **Accuracy (90.8%):** Overall percentage of correct maintenance predictions.
- **Precision (87.2%):** Out of all vehicles flagged for maintenance, how many actually needed it. High precision prevents unnecessary garage expenses.
- **Recall (89.1%):** Out of all vehicles that genuinely required maintenance, how many were caught. High recall prevents dangerous breakdowns.
- **F1-Score (88.2%):** Harmonic mean of Precision and Recall, balancing false alarms against missed breakdowns.

---

### Q12: Why did you choose SQLite and SQLAlchemy?
**Answer:**
- **SQLite:** Serverless, ACID-compliant, self-contained single-file database (`vehiclecare.db`), making the project completely portable for college demonstrations without running external database services.
- **SQLAlchemy ORM:** Provides a clean Object-Relational Mapping abstraction. If this project scales to an enterprise cloud deployment, switching to PostgreSQL or AWS RDS requires changing only the database connection string in `.env`.

---

### Q13: How is FastAPI used and why is it superior to Flask for this project?
**Answer:**
1. **Asynchronous Architecture:** Built on ASGI (Starlette + Uvicorn) for high concurrency.
2. **Automatic Data Validation:** Deep integration with Pydantic v2 validates request bodies and telemetry types automatically.
3. **Auto-Generated Documentation:** Automatically generates interactive Swagger UI (`/docs`) and ReDoc (`/redoc`) specifications.

---

### Q14: How does the frontend communicate with the backend?
**Answer:** The React frontend uses asynchronous `fetch()` calls to the FastAPI REST API at `http://127.0.0.1:8000/api`. The endpoints include `/health`, `/vehicles`, `/predict`, `/agent/analyze`, `/maintenance`, `/dataset/upload`, and `/model/performance`. If the backend is ever stopped, the frontend displays a clear status pill and maintains a graceful client-side fallback mode.

---

### Q15: How can this project be transformed into a commercial industry product?
**Answer:**
1. **Hardware Integration:** Connect an OBD-II dongle (ELM327 / STN1110) to the vehicle's CAN bus to stream real live PID sensor data via Bluetooth or cellular 4G/5G.
2. **IoT Protocol:** Use MQTT or WebSockets to stream telemetry from vehicle edge devices to a cloud-hosted backend.
3. **Fleet Telematics Dashboard:** Multi-tenant dashboard for logistics companies (Amazon, FedEx, Uber) to manage thousands of vehicles.
4. **Remaining Useful Life (RUL) Modeling:** Incorporating survival analysis and Weibull distributions to predict exact remaining kilometers before part failure.
