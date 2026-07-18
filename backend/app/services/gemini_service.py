"""
gemini_service.py — Google Gemini 2.5 Flash Service (Official google-genai SDK)
=================================================================================
Delegates all RAG queries to rag_service.py.
Directly handles operations reports and structured operations answers.
Supports multilingual responses — Gemini auto-detects input language and responds in kind.
"""

import logging
import json
from typing import List, Dict, Any, Optional

try:
    from google import genai
    from google.genai import types
    _GENAI_AVAILABLE = True
except ImportError:
    genai = None
    types = None
    _GENAI_AVAILABLE = False
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Universal multilingual instruction injected into ALL Gemini prompts.
# Gemini detects the user's language and responds in the same language.
# ---------------------------------------------------------------------------
MULTILINGUAL_INSTRUCTION = """

LANGUAGE RULE (MANDATORY):
- Detect the language of the user's input/request.
- Respond ENTIRELY in that same language — including all labels, directions, and descriptions.
- Do NOT switch languages mid-response.
- If the input is in English, respond in English.
- Examples: Spanish input → full Spanish response; Arabic input → full Arabic response.
"""


class GeminiService:
    """
    Thin wrapper around the official Google GenAI SDK.
    - Chat + RAG → delegated to rag_service.query()
    - Operations reports → direct Gemini call with rich prompt
    - Structured ops answers → Gemini with JSON schema output
    """

    def __init__(self):
        self.client: Optional[genai.Client] = None

    def initialize_llm(self) -> bool:
        """Initializes the official Google GenAI Client using the API Key."""
        if not _GENAI_AVAILABLE:
            logger.error(
                "google-genai package is not installed. "
                "Add 'google-genai>=0.5.0' to requirements.txt and redeploy."
            )
            return False
        if not settings.GEMINI_API_KEY:
            logger.warning(
                "GEMINI_API_KEY is not configured in settings. Running in mock/offline mode."
            )
            return False
        try:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            logger.info("Successfully initialized official Google GenAI Client.")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Google GenAI Client: {e}")
            return False

    def _get_client(self) -> Optional[genai.Client]:
        """Returns existing client or attempts initialization."""
        if self.client:
            return self.client
        if self.initialize_llm():
            return self.client
        return None

    # ------------------------------------------------------------------
    # Chat + RAG (delegates to rag_service)
    # ------------------------------------------------------------------

    def get_chat_response(
        self,
        query: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Processes AI Assistant chat using the full RAG pipeline.
        Delegates to rag_service for retrieval + generation.
        """
        # Lazy import to avoid circular dependency at module load time
        from app.services.rag_service import rag_service

        result = rag_service.query(question=query, history=history)
        return {
            "response": result.get("response", "I couldn't generate a response. Please check backend settings."),
            "sources": result.get("sources", []),
            "chunks_used": result.get("chunks_used", 0),
            "mode": result.get("mode", "unknown"),
        }

    # ------------------------------------------------------------------
    # Operations Report (direct Gemini call, no RAG needed)
    # ------------------------------------------------------------------

    def detect_language(self, text: str) -> Dict[str, str]:
        """
        Detects the language of a given text snippet using Gemini.
        Returns {"code": "es", "name": "Spanish"} or {"code": "en", "name": "English"}.
        Falls back gracefully on any error.
        """
        client = self._get_client()
        if not client:
            return {"code": "en", "name": "English"}
        try:
            class LangDetect(BaseModel):
                code: str   # ISO 639-1 two-letter code, e.g. "es", "fr", "ar"
                name: str   # Full English name, e.g. "Spanish", "French", "Arabic"

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"Detect the language of this text and return ONLY a JSON object with 'code' (ISO 639-1) and 'name' (full English name).\n\nText: {text[:300]}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=LangDetect,
                    temperature=0.0,
                )
            )
            return json.loads(response.text)
        except Exception as e:
            logger.warning(f"Language detection failed: {e}")
            return {"code": "en", "name": "English"}

    def generate_ops_report(self, metrics: Dict[str, Any]) -> str:
        """Generates a comprehensive operations status report using Gemini 2.5 Flash."""
        client = self._get_client()
        if not client:
            return (
                "## Operations Report (Mock Mode)\n\n"
                "*Gemini API key is missing. Configure `GEMINI_API_KEY` in `backend/.env` to enable live reports.*"
            )

        prompt = f"""You are the Chief Operations Officer of MetLife Stadium.
Generate a comprehensive, professional Operations Status Report in Markdown format for FIFA World Cup 2026.

Use the following real-time stadium metrics:
- Match: {metrics.get('match_name')}
- Current Score: {metrics.get('score')}
- Elapsed Time: {metrics.get('elapsed_time')}
- Overall Capacity: {metrics.get('capacity')}
- Weather: {metrics.get('weather')}
- Gate Statuses: {metrics.get('gates')}
- Active Security Incidents: {metrics.get('incidents')}

Structure the report with these sections:
1. **Executive Summary** — High-level status snapshot
2. **Crowd & Gate Analysis** — Flow rates, congestion areas, parking
3. **Concessions & Facilities** — Restroom capacity, medical response times, food court load
4. **Security & Incidents Log** — Outstanding incidents, dispatch status
5. **Action Items** — Next operational steps for on-duty staff

Use Markdown formatting (bold, bullet lists, tables). Keep it precise and high-stakes in tone.
Output only the final report content — no preamble.
{MULTILINGUAL_INSTRUCTION}"""
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            logger.error(f"Error generating ops report: {e}")
            return f"Error generating operations report: {e}"

    # ------------------------------------------------------------------
    # Structured Operations Answer (Gemini JSON output schema)
    # ------------------------------------------------------------------

    def get_operations_answer(self, operation: str, user_input: str) -> Dict[str, str]:
        """
        Uses Gemini structured JSON output to answer seat/concession/route queries.
        Retrieves relevant context from ChromaDB via rag_service first.
        """
        client = self._get_client()
        if not client:
            return {
                "location": "N/A",
                "directions": (
                    "Gemini API key is not configured. "
                    "Please set GEMINI_API_KEY in backend/.env and restart the server."
                ),
                "gate": "N/A",
                "walking_time": "N/A",
                "accessible_route": "N/A",
            }

        # Retrieve grounding context from RAG pipeline
        from app.services.rag_service import rag_service
        context, _ = rag_service.retrieve_context(user_input, k=3)

        # Define expected JSON output schema
        class OpsAnswer(BaseModel):
            location: str
            directions: str
            gate: str
            walking_time: str
            accessible_route: str

        prompt = f"""You are a helpful Stadium Operations Guide for MetLife Stadium (FIFA World Cup 2026).
Resolve the following operational request using the retrieved stadium knowledge context.

Operation Type: {operation}
Request: "{user_input}"

Retrieved MetLife Stadium Context:
{context if context else "No specific context available. Use your general knowledge of MetLife Stadium."}

Respond ONLY with a structured JSON object matching the required schema.
- location: Exact place/section/zone that answers the request
- directions: Step-by-step navigation instructions from the nearest gate or concourse
- gate: The nearest gate (Gate A, B, C, or D) for this location
- walking_time: Estimated walking duration from the nearest gate (e.g., '4 mins')
- accessible_route: Step-free path directions using public passenger elevators or ramps (e.g., 'Take Elevator near Section 117 to Level 2'). Specify the closest public elevator (e.g. Near Section 101, 117, 128, 144) for the requested section.
{MULTILINGUAL_INSTRUCTION}"""

        try:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=OpsAnswer,
                temperature=0.1,
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config,
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Error parsing structured operations answer: {e}")
            return {
                "location": "Information Desk (Gate A, Level 1)",
                "directions": f"Please proceed to the Information Desk at Gate A, Level 1 for assistance with: {user_input}",
                "gate": "Gate A",
                "walking_time": "5 mins",
                "accessible_route": "Use elevator at Gate A near Section 101."
            }

    def generate_ai_recommendations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generates dynamic crowd management recommendations using Gemini 2.5 Flash."""
        client = self._get_client()
        if not client:
            # Fallback to rich offline mock recommendations if key is missing
            return {
                "recommendations": [
                    {
                        "title": "Gate B Congestion Relief",
                        "category": "Gate Redirection",
                        "priority": "high",
                        "description": "Gate B is currently at 94% capacity. Deploy shuttle buses to route incoming NJ Transit rail passengers towards Gate C or Gate A.",
                        "action_text": "Redirect Traffic"
                    },
                    {
                        "title": "Staff Section 202 Security Zone",
                        "category": "Crowd Management",
                        "priority": "high",
                        "description": "Due to active incident (Unattended Bag), allocate 4 security stewards to Section 202 perimeter.",
                        "action_text": "Deploy Stewards"
                    },
                    {
                        "title": "Volunteer Concessions Load Balancing",
                        "category": "Volunteer Allocation",
                        "priority": "medium",
                        "description": "Food court near Section 224 is experiencing peak queues. Reallocate 5 volunteers from the Lower Concourse info desk to assist with order pick-ups.",
                        "action_text": "Assign Volunteers"
                    }
                ]
            }

        # Structured schema mapping
        from app.models.schemas import RecommendationsResponse

        prompt = f"""You are the AI Command Center for MetLife Stadium (FIFA World Cup 2026).
Analyze the current live stadium metrics and generate 3 smart, actionable crowd management recommendations.

Live Stadium State:
- Gate/Facilities Capacities: {data.get('gates')}
- Entry Rates (P/Sec): {data.get('entry_rates')}
- Active Security Incidents: {data.get('incidents')}

Generate recommendations covering these categories:
1. Gate Redirection (for congested gates like Gate B)
2. Volunteer/Staff Allocation (for busy stands or concessions)
3. Crowd Management/Security (mitigations for active incidents or density spikes)

Ensure each recommendation is concrete, references specific gates/sections, and contains:
- title: Action-oriented title (e.g., 'Redirect Gate B Traffic')
- category: One of 'Gate Redirection', 'Volunteer Allocation', 'Crowd Management', 'Security'
- priority: 'high', 'medium', or 'low'
- description: Detailed, professional explanation of the operational step
- action_text: Short text for button action (e.g., 'Deploy Volunteers', 'Reroute Passengers')

Respond ONLY with a structured JSON object matching the required schema.
"""

        try:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=RecommendationsResponse,
                temperature=0.2,
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=config,
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {e}")
            return {
                "recommendations": [
                    {
                        "title": "Gate B Congestion Relief",
                        "category": "Gate Redirection",
                        "priority": "high",
                        "description": "Gate B is experiencing heavy traffic. Redirect incoming passengers to Gate A.",
                        "action_text": "Reroute Gate B"
                    }
                ]
            }


# Singleton instance
gemini_service = GeminiService()
