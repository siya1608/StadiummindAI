import os
import uvicorn
from app.config import settings

if __name__ == "__main__":
    # Disable reload in production (Docker/Railway) to avoid file-watcher inotify exhaustion crashes
    should_reload = os.getenv("RELOAD", "false").lower() == "true"
    
    print(f"Starting StadiumMind AI Backend on http://{settings.HOST}:{settings.PORT} (reload={should_reload})")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=should_reload
    )
