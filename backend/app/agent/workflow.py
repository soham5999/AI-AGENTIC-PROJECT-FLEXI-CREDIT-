import json
import time
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.config import settings
from app.agent.tools import (
    get_vehicle_information_tool,
    predict_vehicle_maintenance_tool,
    analyze_vehicle_health_tool,
    get_maintenance_history_tool,
    save_prediction_tool,
    search_tavily_bulletins_tool
)

def run_vehiclecare_agent(
    query: str,
    vehicle_id: str,
    db: Session,
    custom_parameters: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Orchestrates the autonomous VehicleCare AI Agent workflow:
    1. Check & retrieve stored vehicle parameters from SQLite (Tool 5)
    2. Execute ML Random Forest inference (Tool 1)
    3. Analyze subsystem component thresholds (Tool 2)
    4. Retrieve maintenance history (Tool 3)
    5. Query Tavily API for OEM service advisories if key exists
    6. Persist structured prediction record (Tool 4)
    7. Generate AI reasoning and action plan using Groq Llama-3.3 (or Fallback Engine)
    """
    execution_steps = []
    tools_called = []
    step_id = 1

    # ----------------------------------------------------
    # Step 1: Tool 5 - get_vehicle_information
    # ----------------------------------------------------
    step_1 = {
        "id": step_id,
        "toolName": "get_vehicle_information",
        "description": f"Querying SQLite database for vehicle record ID: {vehicle_id}",
        "status": "completed"
    }
    execution_steps.append(step_1)
    tools_called.append("get_vehicle_information")
    step_id += 1

    vehicle_info = get_vehicle_information_tool(vehicle_id, db)
    # Allow overriding with custom parameters if user modified them in form
    if custom_parameters:
        vehicle_info.update(custom_parameters)

    # ----------------------------------------------------
    # Step 2: Tool 1 - predict_vehicle_maintenance
    # ----------------------------------------------------
    step_2 = {
        "id": step_id,
        "toolName": "predict_vehicle_maintenance",
        "description": "Executing Scikit-Learn Random Forest prediction model on telemetry vector",
        "status": "completed"
    }
    execution_steps.append(step_2)
    tools_called.append("predict_vehicle_maintenance")
    step_id += 1

    ml_prediction = predict_vehicle_maintenance_tool(vehicle_info)
    probability = float(ml_prediction.get("probability", 50.0))
    risk_level = ml_prediction.get("riskLevel", "MEDIUM")

    # ----------------------------------------------------
    # Step 3: Tool 2 - analyze_vehicle_health
    # ----------------------------------------------------
    step_3 = {
        "id": step_id,
        "toolName": "analyze_vehicle_health",
        "description": "Evaluating individual subsystem sensor thresholds (battery, brakes, oil, temp)",
        "status": "completed"
    }
    execution_steps.append(step_3)
    tools_called.append("analyze_vehicle_health")
    step_id += 1

    health_analysis = analyze_vehicle_health_tool(vehicle_info)
    affected_subsystems = health_analysis.get("affected_subsystems", [])

    # ----------------------------------------------------
    # Step 4: Tool 3 - get_maintenance_history
    # ----------------------------------------------------
    step_4 = {
        "id": step_id,
        "toolName": "get_maintenance_history",
        "description": "Retrieving historical maintenance logs to calculate service intervals",
        "status": "completed"
    }
    execution_steps.append(step_4)
    tools_called.append("get_maintenance_history")
    step_id += 1

    maint_history = get_maintenance_history_tool(vehicle_id, db)

    # ----------------------------------------------------
    # Step 5: Optional Tavily Bulletin Search
    # ----------------------------------------------------
    tavily_insights = []
    if settings.TAVILY_API_KEY and settings.TAVILY_API_KEY.strip() != "":
        step_tavily = {
            "id": step_id,
            "toolName": "search_tavily_bulletins",
            "description": f"Querying Tavily for {vehicle_info.get('make')} {vehicle_info.get('model')} Technical Service Bulletins",
            "status": "completed"
        }
        execution_steps.append(step_tavily)
        tools_called.append("search_tavily_bulletins")
        step_id += 1
        tavily_insights = search_tavily_bulletins_tool(
            vehicle_info.get("make", "Toyota"),
            vehicle_info.get("model", "Camry"),
            vehicle_info.get("year", 2021),
            query
        )

    # ----------------------------------------------------
    # Step 6: Tool 4 - save_prediction
    # ----------------------------------------------------
    step_save = {
        "id": step_id,
        "toolName": "save_prediction",
        "description": "Persisting structured agent reasoning output to database predictions table",
        "status": "completed"
    }
    execution_steps.append(step_save)
    tools_called.append("save_prediction")

    save_result = save_prediction_tool(vehicle_id, ml_prediction, db)

    # ----------------------------------------------------
    # Step 7: Reasoning & Recommendation Synthesis
    # ----------------------------------------------------
    agent_mode = "Demo Rule-Based Fallback"
    reasoning_text = ""
    recommendations = []

    # Attempt Groq API if key is present
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip() != "":
        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)

            system_prompt = (
                "You are VehicleCare AI, an expert automotive predictive maintenance diagnostic agent. "
                "You are provided with real ML model prediction metrics and telemetry sensor data from a vehicle. "
                "Synthesize a clear, professional reasoning summary (max 3 sentences) and 2 to 4 prioritized action items. "
                "Respond ONLY with valid JSON in the following format:\n"
                "{\n"
                '  "reasoningText": "...",\n'
                '  "recommendations": [\n'
                '     {"action": "...", "priority": "Urgent"|"High"|"Medium"|"Low", "timeframe": "Within X days"}\n'
                "  ]\n"
                "}"
            )

            user_context = {
                "user_query": query,
                "vehicle": vehicle_info,
                "ml_probability": probability,
                "risk_level": risk_level,
                "affected_subsystems": affected_subsystems,
                "service_history_count": maint_history.get("record_count", 0),
                "tavily_insights": tavily_insights
            }

            completion = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(user_context)}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            parsed = json.loads(completion.choices[0].message.content)
            reasoning_text = parsed.get("reasoningText", "")
            recommendations = parsed.get("recommendations", [])
            agent_mode = f"Groq AI Agent ({settings.GROQ_MODEL})"
        except Exception as e:
            # Fall back safely if API call fails
            agent_mode = "Demo Rule-Based Fallback (Groq API Error/Fallback)"

    # Rule-based fallback if Groq is not used or failed
    if not reasoning_text:
        brake_wear = vehicle_info.get("brake_wear_pct", 78)
        oil_life = vehicle_info.get("oil_life_pct", 22)
        days_service = vehicle_info.get("days_since_service", 195)
        battery_volt = vehicle_info.get("battery_voltage", 11.9)

        if probability >= 70:
            reasoning_text = (
                f"The AI Agent determined a HIGH risk of vehicle component failure ({probability}% ML probability). "
                f"The primary contributing factors are critical brake friction wear ({brake_wear}%), depleted oil life ({oil_life}%), "
                f"and an elapsed service duration of {days_service} days."
            )
            recommendations = [
                {"action": f"Replace front and rear brake pads (wear at {brake_wear}%)", "priority": "Urgent", "timeframe": "Within 3 days"},
                {"action": f"Perform complete synthetic engine oil and filter flush (oil life {oil_life}%)", "priority": "High", "timeframe": "Within 7 days"},
                {"action": f"Perform battery load diagnostic and alternator test (voltage at {battery_volt}V)", "priority": "Medium", "timeframe": "Within 14 days"}
            ]
        elif probability >= 35:
            reasoning_text = (
                f"The vehicle health is currently MODERATE ({probability}% risk). "
                f"While operational, key preventive maintenance is required to prevent accelerated wear on braking and lubrication assemblies."
            )
            recommendations = [
                {"action": "Schedule routine oil change and filter replacement", "priority": "Medium", "timeframe": "Within 14 days"},
                {"action": "Inspect brake pad thickness and clean caliper slide pins", "priority": "Medium", "timeframe": "Within 30 days"}
            ]
        else:
            reasoning_text = (
                f"Vehicle telemetry indicates OPTIMAL operating condition ({probability}% risk score). "
                f"All vital powertrain, electrical, and braking parameters remain well within manufacturer safety margins."
            )
            recommendations = [
                {"action": "Maintain routine driving schedule and check tire pressures monthly", "priority": "Low", "timeframe": "Routine"}
            ]

    health_score = max(10, int(round(100 - probability)))

    return {
        "healthScore": health_score,
        "riskLevel": risk_level,
        "probability": probability,
        "reasoningText": reasoning_text,
        "recommendations": recommendations,
        "affectedCount": len(affected_subsystems),
        "executionSteps": execution_steps,
        "agentMode": agent_mode,
        "toolsCalled": tools_called,
        "tavilyInsights": tavily_insights
    }
