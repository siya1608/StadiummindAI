# ============================================================
# StadiumMind AI — Production Dockerfile
# Targets: Railway / Render (backend FastAPI service)
# Supports both root-repository and subfolder-backend build contexts
# ============================================================

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configure python path to find 'app' folder regardless of whether build context
# was the repository root (copies backend/app) or the backend folder directly (copies app)
ENV PYTHONPATH=/app:/app/backend

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt flexibly depending on build context
COPY requirements.txt* backend/requirements.txt* ./
RUN pip install --upgrade pip --root-user-action=ignore && \
    pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

# Copy all files
COPY . .

# Ensure data & chroma directories exist in all potential paths
RUN mkdir -p /app/data/chroma_db /app/backend/data/chroma_db

# Expose default port
EXPOSE 8000

# Start FastAPI app using the production-optimized run.py script
# This automatically reads $PORT from the environment (Railway/Render)
CMD ["python3", "run.py"]
