import random
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.models.schemas import GateStatus, CrowdCapacityResponse, Incident, IncidentCreateRequest

class CrowdController:
    def __init__(self):
        # Gate capacities initial states
        self.capacities = {
            "Gate A": {"location": "North Concourse", "percentage": 72, "style": "normal"},
            "Gate B": {"location": "HEAVY TRAFFIC", "percentage": 94, "style": "danger"},
            "Food Court": {"location": "Level 2 South", "percentage": 45, "style": "normal"},
            "Parking": {"location": "Main Lot", "percentage": 88, "style": "normal"},
        }
        
        self.medical_wait = 2  # minutes
        self.washroom_status = "Normal"

        # Security Incidents
        self.incidents = [
            Incident(
                id="inc_1",
                title="Unattended Bag - Section 202",
                description="Response Unit 04 dispatched",
                timestamp="1m ago",
                level="error",
                status="active"
            ),
            Incident(
                id="inc_2",
                title="Elevator Maintenance - North Stand",
                description="Scheduled check complete",
                timestamp="15m ago",
                level="info",
                status="resolved"
            )
        ]

        # Entry Rate Chart Data (People/Sec)
        self.entry_rates = [60, 80, 95, 40, 20, 55, 90, 70]
        
        # Accessibility Settings
        self.accessibility_settings = {
            "wheelchair_mode": False,
            "low_vision_mode": False,
            "voice_mode": False,
            "large_text": False
        }

    def get_gates_capacity(self) -> CrowdCapacityResponse:
        """Returns gates and facilities capacity data with dynamic variation."""
        gates_list = []
        
        # Simulate slight changes in sensor data
        for name, info in self.capacities.items():
            current_pct = info["percentage"]
            
            # Allow minor fluctuations (-2% to +2%)
            variation = random.randint(-2, 2)
            new_pct = min(max(current_pct + variation, 0), 100)
            
            # Update internal state
            self.capacities[name]["percentage"] = new_pct
            
            # Adjust styling based on percentages
            style = "normal"
            location = info["location"]
            if name == "Gate B" and new_pct > 90:
                style = "danger"
                location = "HEAVY TRAFFIC"
            elif new_pct > 85:
                style = "warning"
            
            gates_list.append(GateStatus(
                name=name,
                location=location,
                percentage=new_pct,
                status_text=f"{new_pct}%",
                style=style
            ))

        # Add Medical and Washroom manually as special cases
        # Fluctuate medical wait time occasionally
        if random.random() < 0.2:
            self.medical_wait = max(1, self.medical_wait + random.choice([-1, 1]))

        gates_list.append(GateStatus(
            name="Medical",
            location="Zone 4 Station",
            percentage=20, # Static progress bar mapping
            status_text=f"{self.medical_wait} min Wait",
            style="normal"
        ))

        gates_list.append(GateStatus(
            name="Washroom",
            location="Universal",
            percentage=50,
            status_text=self.washroom_status,
            style="normal"
        ))

        return CrowdCapacityResponse(gates=gates_list)

    def get_entry_rates(self) -> List[int]:
        """Fluctuates chart data to show active visual updates."""
        # Shift rates and append a new reading
        self.entry_rates.pop(0)
        # Generate new entry rate around 50-100
        new_rate = random.randint(30, 98)
        self.entry_rates.append(new_rate)
        return self.entry_rates

    def get_incidents(self) -> List[Incident]:
        """Returns security incidents."""
        return self.incidents

    def create_incident(self, request: IncidentCreateRequest) -> Incident:
        """Adds a new security incident."""
        new_id = f"inc_{len(self.incidents) + 1}"
        new_incident = Incident(
            id=new_id,
            title=request.title,
            description=request.description,
            timestamp="Just now",
            level=request.level,
            status="active"
        )
        # Insert at the beginning of the list to show first
        self.incidents.insert(0, new_incident)
        return new_incident

    def update_accessibility(self, settings_dict: Dict[str, bool]) -> Dict[str, bool]:
        """Saves accessibility selections."""
        for k, v in settings_dict.items():
            if k in self.accessibility_settings:
                self.accessibility_settings[k] = v
        return self.accessibility_settings

crowd_controller = CrowdController()
