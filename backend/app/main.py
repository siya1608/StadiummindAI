import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router
from app.services.rag_service import rag_service
from app.services.gemini_service import gemini_service
from app.config import settings

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("stadium_mind_backend")

# Initialize FastAPI
app = FastAPI(
    title="StadiumMind AI – FIFA World Cup 2026 Backend",
    description=(
        "FastAPI operations backend powered by Google Gemini 2.5 Flash, "
        "LangChain, and ChromaDB for Retrieval-Augmented Generation."
    ),
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Initializes the full RAG pipeline and Gemini service on startup.

    Steps:
      1. RAG Service (LangChain + ChromaDB):
         - Loads all .txt / .md documents from /data
         - Splits into chunks with RecursiveCharacterTextSplitter
         - Embeds via text-embedding-004 (Google GenAI SDK)
         - Stores in persistent ChromaDB vector store
      2. Gemini Service:
         - Validates API key and initializes google-genai Client
    """
    logger.info("=" * 60)
    logger.info("StadiumMind AI — Starting up...")
    logger.info("=" * 60)

    # 1. Initialize RAG Pipeline (LangChain + ChromaDB)
    logger.info("Initializing RAG Pipeline (LangChain + ChromaDB)...")
    rag_ok = rag_service.initialize()
    if rag_ok:
        status = rag_service.get_status()
        logger.info(
            f"✅ RAG Pipeline ready — {status['vector_count']} vectors indexed, "
            f"documents: {status['loaded_documents']}"
        )
    else:
        logger.warning(
            "⚠️  RAG Pipeline not initialized — GEMINI_API_KEY may be missing. "
            "Running in mock mode."
        )

    # 2. Initialize Gemini LLM Client
    logger.info("Initializing Google Gemini service...")
    llm_ok = gemini_service.initialize_llm()
    if llm_ok:
        logger.info("✅ Google Gemini 2.5 Flash client initialized.")
    else:
        logger.warning("⚠️  Gemini service not initialized — check API key in backend/.env")

    logger.info("=" * 60)
    logger.info(f"StadiumMind AI is live at http://{settings.HOST}:{settings.PORT}")
    logger.info(f"API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 60)


# -------------------------------------------------
# Root & Health Endpoints
# -------------------------------------------------

@app.get("/", tags=["Health"])
def read_root():
    return {
        "status": "online",
        "service": "StadiumMind AI API",
        "version": "2.0.0",
        "stadium": "MetLife Stadium",
        "docs": "/docs",
        "rag_ready": rag_service.is_ready,
    }


@app.get("/health", tags=["Health"])
def health_check():
    rag_status = rag_service.get_status()
    return {
        "status": "healthy",
        "rag_pipeline": rag_status,
        "gemini_client": gemini_service.client is not None,
    }


@app.post("/rag/reindex", tags=["RAG"])
def reindex_knowledge():
    """Force a full re-indexing of all documents in the /data folder."""
    success = rag_service.reindex()
    status = rag_service.get_status()
    return {
        "success": success,
        "message": "Re-indexing complete." if success else "Re-indexing failed (check API key and /data folder).",
        "rag_status": status,
    }


@app.get("/rag/status", tags=["RAG"])
def rag_status():
    """Returns current status of the RAG pipeline."""
    return rag_service.get_status()


# Register all API routes
app.include_router(api_router)
