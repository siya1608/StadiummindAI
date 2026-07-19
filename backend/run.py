import os
import uvicorn

if __name__ == "__main__":
    # Ensure port and host are read directly from environment variables (standard for Railway/Render)
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    should_reload = os.getenv("RELOAD", "false").lower() == "true"
    
    print(f"Starting StadiumMind AI Backend on http://{host}:{port} (reload={should_reload})")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=should_reload
    )

