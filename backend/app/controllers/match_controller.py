from datetime import datetime
from typing import Dict, Any
from app.models.schemas import MatchHUDResponse, MatchScore

class MatchController:
    def __init__(self):
        self.team_a = "USA"
        self.team_b = "MEX"
        self.score_a = 2
        self.score_b = 1
        self.elapsed_minutes = 45
        self.capacity = 82500
        self.weather_temp = 24
        self.weather_condition = "Clear"
        self.status = "LIVE HUD"
        self.camera_name = "West Wing A1"
        self.camera_image_url = "https://lh3.googleusercontent.com/aida-public/AB6AXuC_zkWJOFLm7-Bbv1XbZl3LTcyUU5Ux11uEqZdYlb7w-oNziJ89tfCFm-s9nKNLhqqIAaomXn7yRiZOixP2d4_1s5v9jF6OAXGtB6J5we2gdzDrFOrn2lKiG6JCB5m68jnmDMFpx81_m1ESWhx1VsuX_zCFPrnqe52jKEW5RNO4Hr1gc923wfLqIsNqSQQz5rlJxNEOUkdojrLAlhGVh_mu4wJtMy4QdEbJoPRFf5BEFoH8G15-Uciw"

    def get_hud_data(self) -> MatchHUDResponse:
        """Returns the current HUD data including marquee feeds."""
        # Simple simulated timer update
        now = datetime.now()
        # Increment minutes slowly based on seconds to make it feel alive
        elapsed = f"{self.elapsed_minutes}:{now.second:02d}"

        # Current marquee alerts
        marquee_alerts = [
            {"type": "MATCH", "content": f"MATCH FEED: {self.elapsed_minutes}' substitution for USA. Christian Pulisic out, Giovanni Reyna in."},
            {"type": "TRANSPORT", "content": "TRANSPORT: MetLife Express shuttle arriving in 4 mins at Gate C."},
            {"type": "EMERGENCY", "content": "EMERGENCY CONTACT: Dial *911 for in-stadium security assist."},
            {"type": "WEATHER", "content": f"WEATHER: {self.weather_temp}°C, Humidity 45%, Wind NW at 12km/h."}
        ]

        return MatchHUDResponse(
            team_a=self.team_a,
            team_b=self.team_b,
            score=MatchScore(usa=self.score_a, mex=self.score_b),
            elapsed_time=elapsed,
            capacity=self.capacity,
            weather=f"{self.weather_temp}°C {self.weather_condition}",
            status=self.status,
            primary_camera={
                "name": self.camera_name,
                "url": self.camera_image_url
            },
            marquee_alerts=marquee_alerts
        )

    def increment_score(self, team: str) -> MatchScore:
        """Helper to dynamically update scores during the match."""
        if team.upper() == "USA":
            self.score_a += 1
        elif team.upper() == "MEX":
            self.score_b += 1
        return MatchScore(usa=self.score_a, mex=self.score_b)

    def update_match_time(self, minutes: int):
        """Updates elapsed match time."""
        self.elapsed_minutes = min(max(minutes, 0), 120)

match_controller = MatchController()
