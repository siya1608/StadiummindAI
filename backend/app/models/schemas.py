from pydantic import BaseModel, Field
from typing import List, Optional, Dict

# Match HUD schemas
class MatchScore(BaseModel):
    usa: int
    mex: int

class MatchHUDResponse(BaseModel):
    team_a: str = "USA"
    team_b: str = "MEX"
    score: MatchScore
    elapsed_time: str
    capacity: int
    weather: str
    status: str
    primary_camera: Dict[str, str]
    marquee_alerts: List[Dict[str, str]]

# Gate/Area status schemas
class GateStatus(BaseModel):
    name: str
    location: str
    percentage: int
    status_text: str
    style: str  # e.g., 'normal', 'warning', 'danger'

class CrowdCapacityResponse(BaseModel):
    gates: List[GateStatus]

# Incident schemas
class Incident(BaseModel):
    id: str
    title: str
    description: str
    timestamp: str
    level: str  # 'warning', 'info', 'error'
    status: str  # 'active', 'resolved'

class IncidentCreateRequest(BaseModel):
    title: str
    description: str
    level: str

# Assistant schemas
class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[str]
    detected_language: Optional[str] = None   # e.g. "Spanish", "French", "English"

# Operations schemas
class FindSeatRequest(BaseModel):
    ticket: str
    accessible_requested: Optional[bool] = False

class FindSeatResponse(BaseModel):
    location: str
    directions: str
    gate: str
    walking_time: str
    accessible_route: str

class FoodRecRequest(BaseModel):
    preference: str
    location: Optional[str] = None

class ConcessionRec(BaseModel):
    name: str
    location: str
    menu_highlights: List[str]
    description: str

class FoodRecResponse(BaseModel):
    recommendations: List[ConcessionRec]

class WashroomStatusResponse(BaseModel):
    universal: str
    queue_time: str
    status: str

class EmergencyRequest(BaseModel):
    issue: str
    location: str

class EmergencyResponse(BaseModel):
    status: str
    message: str
    dispatch_unit: str
    timestamp: str

class TransportItem(BaseModel):
    type: str
    name: str
    eta: str
    status: str

class TransportResponse(BaseModel):
    status: str
    transport_items: List[TransportItem]

class ReportResponse(BaseModel):
    report_md: str

# Accessibility schemas
class AccessibilityToggleRequest(BaseModel):
    wheelchair_mode: bool
    low_vision_mode: bool
    voice_mode: bool
    large_text: bool

class AccessibilityResponse(BaseModel):
    status: str
    preferences: Dict[str, bool]

# AI Recommendations schemas
class RecommendationItem(BaseModel):
    title: str
    category: str  # e.g., 'Gate Redirection', 'Volunteer Allocation', 'Crowd Management'
    priority: str  # 'high', 'medium', 'low'
    description: str
    action_text: str

class RecommendationsResponse(BaseModel):
    recommendations: List[RecommendationItem]

