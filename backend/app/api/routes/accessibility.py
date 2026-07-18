from fastapi import APIRouter
from app.models.schemas import AccessibilityToggleRequest, AccessibilityResponse
from app.controllers.crowd_controller import crowd_controller

router = APIRouter(prefix="/accessibility", tags=["accessibility"])

@router.post("/toggle", response_model=AccessibilityResponse)
def toggle_accessibility(request: AccessibilityToggleRequest) -> AccessibilityResponse:
    """Toggles and saves in-memory preferences for accessibility modes."""
    settings_dict = {
        "wheelchair_mode": request.wheelchair_mode,
        "low_vision_mode": request.low_vision_mode,
        "voice_mode": request.voice_mode,
        "large_text": request.large_text
    }
    updated = crowd_controller.update_accessibility(settings_dict)
    return AccessibilityResponse(
        status="Preferences Updated",
        preferences=updated
    )
