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
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# --- Copy application source ---
COPY . .

# --- Ensure data directory exists (ChromaDB will be built on first boot) ---
RUN mkdir -p /app/data/chroma_db

# Expose the port Render will route to
EXPOSE 8000

# --- Health check ---
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# --- Production start command ---
# Uses gunicorn with uvicorn workers for concurrent request handling
# Render sets HOST=0.0.0.0 and PORT automatically via environment variables
CMD gunicorn app.main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers 2 \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --keep-alive 5 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
