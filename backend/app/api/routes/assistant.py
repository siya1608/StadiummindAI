from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.controllers.assistant_controller import assistant_controller

router = APIRouter(prefix="/assistant", tags=["assistant"])

@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(request: ChatRequest) -> ChatResponse:
    """Chat endpoint supporting chat histories and LangChain RAG queries with Gemini 2.5 Flash."""
    return assistant_controller.chat(request)
