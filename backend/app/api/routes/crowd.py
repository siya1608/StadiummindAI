from fastapi import APIRouter
from typing import List
from app.models.schemas import CrowdCapacityResponse, RecommendationsResponse
from app.controllers.crowd_controller import crowd_controller
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/crowd", tags=["crowd"])

@router.get("/gates", response_model=CrowdCapacityResponse)
def get_gates_capacity() -> CrowdCapacityResponse:
    """Returns real-time crowd occupancy of gate areas and facilities."""
    return crowd_controller.get_gates_capacity()

@router.get("/entry-rates", response_model=List[int])
def get_entry_rates() -> List[int]:
    """Returns the entry rate chart dataset, fluctuating on every call."""
    return crowd_controller.get_entry_rates()

@router.get("/recommendations", response_model=RecommendationsResponse)
def get_ai_recommendations() -> RecommendationsResponse:
    """Uses Google Gemini 2.5 Flash to generate real-time crowd management suggestions based on current gate and incident states."""
    # 1. Fetch current data
    gates = crowd_controller.get_gates_capacity()
    entry_rates = crowd_controller.entry_rates
    incidents = crowd_controller.get_incidents()
    
    # 2. Package data
    data = {
        "gates": [g.dict() for g in gates.gates],
        "entry_rates": entry_rates,
        "incidents": [inc.dict() for inc in incidents]
    }
    
    # 3. Generate dynamic recommendations
    result = gemini_service.generate_ai_recommendations(data)
    return RecommendationsResponse(**result)
