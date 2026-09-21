from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.agent import AgentAnalyzeRequest, AgentAnalyzeResponse
from app.agent.workflow import run_vehiclecare_agent

router = APIRouter(prefix="/agent", tags=["AI Agent"])

@router.post("/analyze", response_model=AgentAnalyzeResponse)
def execute_agent_analysis(payload: AgentAnalyzeRequest, db: Session = Depends(get_db)):
    """
    Executes the multi-tool VehicleCare AI Agent pipeline:
    - Queries database for vehicle telemetry
    - Executes Scikit-Learn prediction tool
    - Analyzes component risk thresholds
    - Retrieves maintenance history
    - Optionally searches Tavily for OEM bulletins
    - Synthesizes reasoned action plan via Groq Llama-3.3 (or Fallback Engine)
    """
    result = run_vehiclecare_agent(
        query=payload.query,
        vehicle_id=payload.vehicle_id or "v-camry-01",
        db=db,
        custom_parameters=payload.custom_parameters
    )
    return result
