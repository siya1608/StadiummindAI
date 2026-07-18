from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import Incident, IncidentCreateRequest
from app.controllers.crowd_controller import crowd_controller

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/incidents", response_model=List[Incident])
def get_incidents() -> List[Incident]:
    """Returns active security incidents logs."""
    return crowd_controller.get_incidents()

@router.post("/incidents", response_model=Incident)
def create_incident(request: IncidentCreateRequest) -> Incident:
    """Creates/Logs a new incident dynamically."""
    if not request.title or not request.level:
        raise HTTPException(status_code=400, detail="Title and level are required.")
    return crowd_controller.create_incident(request)
