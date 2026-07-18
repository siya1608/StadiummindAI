import logging
import concurrent.futures
from app.models.schemas import ChatRequest, ChatResponse
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

class AssistantController:
    def chat(self, request: ChatRequest) -> ChatResponse:
        """Processes AI Assistant queries using RAG context retrieval with multilingual support."""
        # Convert request history (if any) into the expected format
        history_list = []
        if request.history:
            for item in request.history:
                history_list.append({
                    "role": item.role,
                    "content": item.content
                })

        # Run RAG chat + language detection concurrently (no extra latency)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            chat_future = executor.submit(
                gemini_service.get_chat_response,
                query=request.message,
                history=history_list
            )
            lang_future = executor.submit(
                gemini_service.detect_language,
                request.message
            )
            result = chat_future.result()
            lang = lang_future.result()

        detected_language = lang.get("name", "English")

        return ChatResponse(
            response=result.get("response", "I'm sorry, I couldn't generate a response. Please check backend settings."),
            sources=result.get("sources", []),
            detected_language=detected_language
        )

assistant_controller = AssistantController()
