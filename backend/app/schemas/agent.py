from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class AgentAnalyzeRequest(BaseModel):
    query: str = Field(..., example="Perform complete maintenance diagnostic for my vehicle and give action items.")
    vehicle_id: Optional[str] = Field("v-camry-01", example="v-camry-01")
    custom_parameters: Optional[Dict[str, Any]] = None

class AgentStep(BaseModel):
    id: int
    toolName: str
    description: str
    status: str = "completed" # completed, executing, failed
    output: Optional[Dict[str, Any]] = None

class RecommendationItem(BaseModel):
    action: str
    priority: str # Urgent, High, Medium, Low
    timeframe: str # e.g. Within 3 days, Within 14 days

class AgentAnalyzeResponse(BaseModel):
    healthScore: int
    riskLevel: str
    probability: float
    reasoningText: str
    recommendations: List[RecommendationItem]
    affectedCount: int
    executionSteps: List[AgentStep]
    agentMode: str # Groq AI Agent, Tavily-Enriched Agent, or Demo Rule-Based Fallback
    toolsCalled: List[str]
    tavilyInsights: Optional[List[str]] = None
