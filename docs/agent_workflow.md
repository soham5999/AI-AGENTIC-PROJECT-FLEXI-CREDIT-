# Agentic AI Subsystem: Workflow & Tool Execution Guide

## 1. What Makes This An "Agentic AI" Project?
A conventional AI model only produces a raw statistical prediction (e.g. `0.85 probability of failure`). A conventional chatbot simply echoes text without interacting with databases or models.

An **Agentic AI** system, by contrast, exhibits:
1. **Goal-Directed Behavior:** Takes a high-level user objective (e.g. *"Inspect my car before a long road trip"*).
2. **Environment Grounding:** Interacts with external systems (SQLite database, Scikit-Learn ML models, web APIs).
3. **Tool Use (Function Calling):** Autonomously invokes internal software tools in a coordinated sequence.
4. **Synthesis & Actionability:** Interprets raw numerical outputs into human-understandable, prioritized action items with deadlines.

---

## 2. The 5 Agent Tools

| Tool ID | Function Name | Purpose & Action |
| :--- | :--- | :--- |
| **Tool 1** | `predict_vehicle_maintenance` | Executes Scikit-Learn Random Forest inference on the telemetry vector to compute probability and risk level. |
| **Tool 2** | `analyze_vehicle_health` | Checks physical safety thresholds for brake wear, engine temperature, oil life, battery voltage, and tire pressure. |
| **Tool 3** | `get_maintenance_history` | Queries SQLite for past service events, total spend, and days elapsed since certified inspection. |
| **Tool 4** | `save_prediction` | Persists the agent's diagnostic result, probability, and risk level into the `predictions` table. |
| **Tool 5** | `get_vehicle_information` | Retrieves baseline telemetry and vehicle specifications from SQLite for a given vehicle ID. |
| *(Ext)* | `search_tavily_bulletins` | Searches the web via Tavily API for OEM recalls and Technical Service Bulletins (TSB). |

---

## 3. End-to-End Agent Execution Flow

```
User Query: "Perform complete maintenance diagnostic for my vehicle"
   │
   ▼
[ Step 1: Tool 5 - get_vehicle_information ]
   │ Fetches: make="Toyota", model="Camry", brake_wear=78%, oil_life=22%, voltage=11.9V
   ▼
[ Step 2: Tool 1 - predict_vehicle_maintenance ]
   │ Calls Scikit-Learn Random Forest Classifier
   │ Returns: probability = 85.0%, riskLevel = "HIGH", maintenanceRequired = "YES"
   ▼
[ Step 3: Tool 2 - analyze_vehicle_health ]
   │ Identifies 3 anomalies:
   │  - Brake wear at 78% (Critical)
   │  - Oil life at 22% (Moderate)
   │  - Battery voltage at 11.9V (Moderate)
   ▼
[ Step 4: Tool 3 - get_maintenance_history ]
   │ Queries previous oil changes and service intervals (195 days elapsed)
   ▼
[ Step 5: (Optional) search_tavily_bulletins ]
   │ Queries Tavily for Toyota Camry Hybrid Technical Service Bulletins
   ▼
[ Step 6: Tool 4 - save_prediction ]
   │ Commits prediction record to SQLite DB
   ▼
[ Step 7: Reasoning & Recommendation Synthesis ]
   │ If GROQ_API_KEY is present:
   │   Invokes Groq (llama-3.3-70b-versatile) with structured JSON prompt
   │ Else:
   │   Executes high-performance domain-expert Fallback Agent
   ▼
Structured Agent Response to User:
   - Health Score: 15 / 100
   - Risk Level: HIGH
   - Diagnostic Explanation
   - Prioritized Action Items with urgency deadlines (3 days, 7 days, 14 days)
```
