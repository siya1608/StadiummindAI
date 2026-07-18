from fastapi import APIRouter
from app.models.schemas import (
    FindSeatRequest, FindSeatResponse,
    FoodRecRequest, FoodRecResponse,
    WashroomStatusResponse, EmergencyRequest, EmergencyResponse,
    TransportResponse, ReportResponse
)
from app.controllers.operations_controller import operations_controller

router = APIRouter(prefix="/operations", tags=["operations"])

@router.post("/find-seat", response_model=FindSeatResponse)
def find_seat(request: FindSeatRequest) -> FindSeatResponse:
    """Uses Gemini & ChromaDB context to locate seats and give detailed directions."""
    return operations_controller.find_seat(request)

@router.post("/food-recs", response_model=FoodRecResponse)
def get_food_recommendations(request: FoodRecRequest) -> FoodRecResponse:
    """Queries concessions and menus for matching food recommendations."""
    return operations_controller.get_food_recommendations(request)

@router.get("/washroom", response_model=WashroomStatusResponse)
def get_washroom_status() -> WashroomStatusResponse:
    """Returns universal washroom status and queue times."""
    return operations_controller.get_washroom_status()

@router.post("/emergency", response_model=EmergencyResponse)
def trigger_emergency(request: EmergencyRequest) -> EmergencyResponse:
    """Triggers an emergency alert and logs it in Security Incidents."""
    return operations_controller.trigger_emergency(request)

@router.get("/transport", response_model=TransportResponse)
def get_transport_schedule() -> TransportResponse:
    """Returns local transport and shuttle timetables."""
    return operations_controller.get_transport_schedule()

@router.post("/generate-report", response_model=ReportResponse)
def generate_report() -> ReportResponse:
    """Asks Gemini 2.5 Flash to synthesize current match and crowd metrics into a PDF/Markdown report."""
    return operations_controller.generate_report()
