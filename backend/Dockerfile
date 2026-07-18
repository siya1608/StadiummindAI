# ============================================================
# StadiumMind AI — Production Dockerfile
# Target: Render (backend FastAPI service)
# ============================================================

# --- Base image ---
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable stdout/stderr streaming
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Install system dependencies required by ChromaDB (SQLite) and google-genai
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Install Python dependencies ---
# All packages (including gunicorn) are declared in requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip --root-user-action=ignore && \
    pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# --- Copy application source ---
COPY . .

# --- Ensure data & chroma directories exist ---
RUN mkdir -p /app/data/chroma_db

# Expose the port (Render will override via $PORT env var)
EXPOSE 8000

# --- Health check ---
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# --- Production start command (shell form so $PORT is expanded) ---
# 1 worker is optimal for Render's free-tier memory limits.
# Uses uvicorn worker class for ASGI (async) support.
CMD gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 1 \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --keep-alive 5 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
