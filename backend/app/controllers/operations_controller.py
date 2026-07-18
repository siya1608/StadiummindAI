import logging
from typing import Dict, Any, List
from app.models.schemas import (
    FindSeatRequest, FindSeatResponse,
    FoodRecRequest, FoodRecResponse, ConcessionRec,
    WashroomStatusResponse, EmergencyRequest, EmergencyResponse,
    TransportResponse, TransportItem, ReportResponse
)
from app.services.gemini_service import gemini_service
from app.controllers.match_controller import match_controller
from app.controllers.crowd_controller import crowd_controller

logger = logging.getLogger(__name__)

class OperationsController:
    def find_seat(self, request: FindSeatRequest) -> FindSeatResponse:
        """Finds seating location, step-by-step directions, walking times, and accessible routes."""
        query = f"Seat request: {request.ticket}"
        if request.accessible_requested:
            query += " (User requires wheelchair accessible, step-free navigation route)"
            
        result = gemini_service.get_operations_answer("Find Seat & Navigation", query)
        
        return FindSeatResponse(
            location=result.get("location", "Section Not Found"),
            directions=result.get("directions", "Head towards the main outer concourse."),
            gate=result.get("gate", "Gate A"),
            walking_time=result.get("walking_time", "5 mins"),
            accessible_route=result.get("accessible_route", "N/A")
        )

    def get_food_recommendations(self, request: FoodRecRequest) -> FoodRecResponse:
        """Recommends concessions based on preferences using Gemini."""
        # Query Gemini
        result = gemini_service.get_operations_answer("Food Recs", f"Preference: {request.preference}, Location: {request.location or 'anywhere'}")
        
        # We parse the result or output a structured response.
        # To ensure we return a proper list, let's map the returned location and details.
        recs = []
        if isinstance(result, dict) and "location" in result:
            recs.append(ConcessionRec(
                name=result.get("location", "Concession Stand"),
                location=result.get("location", "Concourse Level"),
                menu_highlights=result.get("directions", "").split(",")[:3] if "," in result.get("directions", "") else ["Signature Specials"],
                description=result.get("directions", "Recommending concession stand based on dietary preference.")
            ))
        else:
            # Fallback mock items matching index if Gemini failed
            recs = [
                ConcessionRec(
                    name="Global Grills",
                    location="Level 2 South (near Section 224)",
                    menu_highlights=["Tacos", "Hot Dogs", "Soda"],
                    description="Standard arena favorites with local New Jersey ingredients."
                ),
                ConcessionRec(
                    name="Apex Vegan Burgers",
                    location="Level 2 South (near Section 224)",
                    menu_highlights=["Plant-based Burgers", "Fries", "Water"],
                    description="100% vegan food court specialty stall."
                )
            ]
        
        return FoodRecResponse(recommendations=recs)

    def get_washroom_status(self) -> WashroomStatusResponse:
        """Retrieves universal washroom occupancy."""
        import random
        wait = random.randint(1, 6)
        status = "Normal"
        if wait > 5:
            status = "Busy"
        return WashroomStatusResponse(
            universal="Occupancy: 45%",
            queue_time=f"{wait} min",
            status=status
        )

    def trigger_emergency(self, request: EmergencyRequest) -> EmergencyResponse:
        """Logs emergency incident and returns dispatch unit info."""
        from datetime import datetime
        
        # Log as security incident in crowd controller
        from app.models.schemas import IncidentCreateRequest
        crowd_controller.create_incident(IncidentCreateRequest(
            title=f"EMERGENCY: {request.issue}",
            description=f"Reported at {request.location}. Urgent dispatch initiated.",
            level="error"
        ))

        import random
        unit_num = random.randint(1, 10)
        
        return EmergencyResponse(
            status="CRITICAL DISPATCHED",
            message=f"Emergency services alerted for '{request.issue}' at {request.location}.",
            dispatch_unit=f"Medical Unit {unit_num:02d} / Security Guard Squad Delta",
            timestamp=datetime.now().strftime("%H:%M:%S")
        )

    def get_transport_schedule(self) -> TransportResponse:
        """Retrieves shuttle and transit schedules."""
        import random
        eta_bus = random.randint(2, 6)
        
        items = [
            TransportItem(
                type="shuttle",
                name="MetLife Express Shuttle (Gate C)",
                eta=f"{eta_bus} mins",
                status="On Time"
            ),
            TransportItem(
                type="train",
                name="NJ Transit Rail ( Meadowlands Station)",
                eta="12 mins",
                status="Boarding Soon"
            ),
            TransportItem(
                type="shuttle",
                name="VIP Parking Lot Shuttle (Gate A)",
                eta="8 mins",
                status="Delayed"
            )
        ]
        
        return TransportResponse(
            status="Active Operations",
            transport_items=items
        )

    def generate_report(self) -> ReportResponse:
        """Gathers all controllers' statuses and uses Gemini to synthesize the ops report."""
        hud = match_controller.get_hud_data()
        crowd = crowd_controller.get_gates_capacity()
        incidents = crowd_controller.get_incidents()
        
        # Build prompt context block
        incidents_summary = ", ".join([f"{inc.title} ({inc.status})" for inc in incidents])
        gates_summary = ", ".join([f"{gate.name}: {gate.status_text} ({gate.location})" for gate in crowd.gates])

        metrics_context = {
            "match_name": f"{hud.team_a} VS {hud.team_b}",
            "score": f"{hud.score.usa} - {hud.score.mex}",
            "elapsed_time": hud.elapsed_time,
            "capacity": hud.capacity,
            "weather": hud.weather,
            "gates": gates_summary,
            "incidents": incidents_summary
        }
        
        report_text = gemini_service.generate_ops_report(metrics_context)
        return ReportResponse(report_md=report_text)

operations_controller = OperationsController()
