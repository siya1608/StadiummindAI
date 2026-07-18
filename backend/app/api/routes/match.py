from fastapi import APIRouter
from app.models.schemas import MatchHUDResponse
from app.controllers.match_controller import match_controller

router = APIRouter(prefix="/match", tags=["match"])

@router.get("/hud", response_model=MatchHUDResponse)
def get_hud() -> MatchHUDResponse:
    """Returns the live HUD information for the match, including marquee text."""
    return match_controller.get_hud_data()

@router.post("/score/{team}", response_model=dict)
def increment_score(team: str):
    """Admin endpoint to increment score for USA or MEX."""
    new_score = match_controller.increment_score(team)
    return {"status": "success", "score": new_score}
