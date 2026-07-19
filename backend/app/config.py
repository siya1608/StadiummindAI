import os
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    CHROMA_DB_DIR: str = str(BASE_DIR / "data" / "chroma_db")
    STADIUM_KNOWLEDGE_PATH: str = str(BASE_DIR / "data" / "stadium_knowledge.txt")

    # Server Settings
    # Default 0.0.0.0 for Docker/Render (binds to all interfaces).
    # Render also injects $PORT automatically.
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    CORS_ORIGINS: list[str] = [
        origin.strip() for origin in os.getenv(
            "CORS_ORIGINS",
            "https://stadiummind-ai-6ihz.vercel.app,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,*"
        ).split(",")
        if origin.strip()
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

